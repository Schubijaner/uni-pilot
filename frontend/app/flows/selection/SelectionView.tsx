/**
 * SelectionView - Hauptansicht für die Job-Auswahl
 * Kombiniert Job-Tree und Filter-Fragen
 */

import React, { useState, useMemo, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router';
import { Layout } from '~/components/layout';
import { Button, Card } from '~/components/ui';
import { useApp } from '~/contexts';
import { FilterQuestions } from './components/FilterQuestions';
import CareerTree from '~/components/ui/Tree/Tree';
import { getUserQuestions } from '~/api/getUserQuestions';
import type { UserQuestion } from '~/types';
import { getTree } from '~/api/getTree';
import ChatContainer from '~/components/ui/ChatContainer';

interface TreeNode {
  id: number;
  name: string;
  description: string;
  is_leaf: boolean;
  level: number;
  children: TreeNode[];
  topic_field_id: number | null;
  questions: string[] | null;
}

interface TreeData {
  study_program_id: number;
  nodes: TreeNode[]; // Nach Normalisierung durch getTree ist dies immer ein Array
}

interface QuestionNode {
  question: string;
  nodeId: number;
  children: QuestionNode[];
}

function transformTreeToFlow(data: TreeData | null, onNodeClick: (node: TreeNode, event: React.MouseEvent) => void): { nodes: any[]; edges: any[] } {
  const nodes: any[] = [];
  const edges: any[] = [];
  
  // Safety check: return empty if data is invalid
  if (!data || !data.nodes || !Array.isArray(data.nodes)) {
    return { nodes, edges };
  }

  const xSpacing = 250;
  const ySpacing = 150;

  // First pass: calculate subtree widths
  const getSubtreeWidth = (node: TreeNode): number => {
    if (!node.children || node.children.length === 0) {
      return 1; // Leaf nodes have width of 1
    }
    // Sum of all children's subtree widths
    return node.children.reduce((sum, child) => sum + getSubtreeWidth(child), 0);
  };

  // Second pass: position nodes based on subtree widths
  const processNode = (
    node: TreeNode, 
    parentId: string | null, 
    leftBound: number,  // Left edge of available space
    rightBound: number  // Right edge of available space
  ) => {
    const nodeId = `n${node.id}`;
    
    // Center node in its available space
    const x = (leftBound + rightBound) / 2;
    const y = node.level * ySpacing;
    
    nodes.push({
      id: nodeId,
      position: { x, y },
      data: { label: node.name, description: node.description,
        onClick: (event: React.MouseEvent) => onNodeClick(node, event)
       },
      type: node.is_leaf ? "custom-leaf" : "custom-root",
    });
    
    if (parentId) {
      edges.push({
        id: `${parentId}-${nodeId}`,
        source: parentId,
        target: nodeId,
        style: { stroke: '#6366f1', strokeWidth: 2 }
      });
    }
    
    // Process children with proportional space allocation
    if (node.children && Array.isArray(node.children) && node.children.length > 0) {
      const totalWidth = rightBound - leftBound;
      const childWidths = node.children.map(child => getSubtreeWidth(child));
      const totalChildWidth = childWidths.reduce((sum, w) => sum + w, 0);
      
      let currentLeft = leftBound;
      
      node.children.forEach((child, index) => {
        // Allocate space proportionally based on subtree width
        const childSpace = (childWidths[index] / totalChildWidth) * totalWidth;
        const childRight = currentLeft + childSpace;
        
        processNode(child, nodeId, currentLeft, childRight);
        
        currentLeft = childRight;
      });
    }
  };
  
  // Calculate total width needed
  const totalTreeWidth = data.nodes.reduce((sum, node) => sum + getSubtreeWidth(node), 0);
  const totalWidthPixels = totalTreeWidth * xSpacing;
  
  // Process root nodes
  let currentLeft = 0;
  data.nodes.forEach((node) => {
    const nodeWidth = getSubtreeWidth(node);
    const nodeSpace = (nodeWidth / totalTreeWidth) * totalWidthPixels;
    const nodeRight = currentLeft + nodeSpace;
    
    processNode(node, null, currentLeft, nodeRight);
    
    currentLeft = nodeRight;
  });
  
  return { nodes, edges };
}

// Filter tree based on user's selected answers
function filterTreeByAnswers(
  nodes: TreeNode[] | undefined,
  selectedOptions: Record<string, boolean>
): TreeNode[] {
  if (!nodes || !Array.isArray(nodes)) {
    return [];
  }
  
  return nodes
    .filter((node) => {
      // Check if any of this node's questions were answered with "false"
      if (node.questions && Array.isArray(node.questions)) {
        for (const question of node.questions) {
          // If this question was answered with false, filter out this node
          if (selectedOptions[question] === false) {
            return false;
          }
        }
      }
      return true;
    })
    .map((node) => {
      // Recursively filter children
      const filteredChildren = filterTreeByAnswers(node.children, selectedOptions);

      // Return node with filtered children
      return {
        ...node,
        children: filteredChildren,
      };
    });
}

// Helper function to collect all leaf nodes from the tree
function collectLeafNodes(nodes: TreeNode[]): TreeNode[] {
  const leaves: TreeNode[] = [];
  
  const traverse = (nodeList: TreeNode[]) => {
    for (const node of nodeList) {
      if (node.is_leaf) {
        leaves.push(node);
      } else {
        traverse(node.children);
      }
    }
  };
  
  traverse(nodes);
  return leaves;
}

// Build question tree from tree nodes - preserving hierarchy
function buildQuestionTree(nodes: TreeNode[]): QuestionNode[] {
  const questionNodes: QuestionNode[] = [];
  
  const processNode = (node: TreeNode): QuestionNode[] => {
    const result: QuestionNode[] = [];
    
    // Process children first to get their question nodes
    const childQuestionNodes: QuestionNode[] = [];
    if (node.children && Array.isArray(node.children)) {
      for (const child of node.children) {
        childQuestionNodes.push(...processNode(child));
      }
    }
    
    // If this node has questions, create question nodes with children's questions as children
    if (node.questions && Array.isArray(node.questions) && node.questions.length > 0) {
      // For each question in this node, create a question node
      // The last question gets the children
      for (let i = 0; i < node.questions.length; i++) {
        const isLastQuestion = i === node.questions.length - 1;
        result.push({
          question: node.questions[i],
          nodeId: node.id,
          children: isLastQuestion ? childQuestionNodes : [],
        });
      }
    } else {
      // No questions at this node, just pass through children's questions
      result.push(...childQuestionNodes);
    }
    
    return result;
  };
  
  for (const node of nodes) {
    questionNodes.push(...processNode(node));
  }
  
  return questionNodes;
}

// Flatten visible questions based on selected answers
function getVisibleQuestions(
  questionTree: QuestionNode[],
  selectedOptions: Record<string, boolean>
): string[] {
  const visibleQuestions: string[] = [];
  
  const traverse = (nodes: QuestionNode[]) => {
    for (const node of nodes) {
      visibleQuestions.push(node.question);
      
      // Only show children if this question was answered with "true"
      if (selectedOptions[node.question] === true && node.children.length > 0) {
        traverse(node.children);
      }
    }
  };
  
  traverse(questionTree);
  return visibleQuestions;
}

export const SelectionView: React.FC = () => {
  const navigate = useNavigate();
  const { state, toggleJob, generateRoadmap, token } = useApp();
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedOptions, setSelectedOptions] = useState<Record<string, boolean>>({});
  const [questionTree, setQuestionTree] = useState<QuestionNode[]>([]);
  const [isLoadingTree, setIsLoadingTree] = useState(true);
  const [isLoadingQuestions, setIsLoadingQuestions] = useState(true);
  const [treeError, setTreeError] = useState<string | null>(null);

  const [treeData, setTreeData] = useState<TreeData | null>(null);

  const [popupContent, setPopupContent] = useState<{ 
    title: string; 
    description: string;
    topicFieldId?: number;
  } | null>(null);

  const handleNodeClick = useCallback((node: TreeNode, event: React.MouseEvent) => {
    setPopupContent({
      title: node.name,
      description: node.description,
      topicFieldId: node.topic_field_id ? node.topic_field_id : undefined,
    });
  }, []);

  useEffect(() => {
    const fetchTree = async () => {
      setIsLoadingTree(true);
      setIsLoadingQuestions(true);
      setTreeError(null);
      try {
        const studyProgramId = 1;
        const token = localStorage.getItem('auth_token') || undefined;
        const response = await getTree(studyProgramId, token);
        if (response && response.nodes) {
          setTreeData(response);
          
          // Build question tree from tree nodes
          const builtQuestionTree = buildQuestionTree(response.nodes);
          setQuestionTree(builtQuestionTree);
        } else {
          console.error('Invalid tree data structure:', response);
          setTreeData(null);
          setTreeError('Ungültige Datenstruktur vom Server');
          setQuestionTree([]);
        }
      } catch (error) {
        console.error('Failed to fetch tree:', error);
        setTreeData(null);
        setTreeError('Fehler beim Laden des Karrierebaums');
        setQuestionTree([]);
      } finally {
        setIsLoadingTree(false);
        setIsLoadingQuestions(false);
      }
    };
    fetchTree();
  }, [token]);

  // Get visible questions based on answers
  const visibleQuestions = useMemo(() => {
    return getVisibleQuestions(questionTree, selectedOptions);
  }, [questionTree, selectedOptions]);

  // Filter the tree based on user's answers
  const filteredTreeData = useMemo(() => {
    if (!treeData || !treeData.nodes || !Array.isArray(treeData.nodes)) {
      return null;
    }
    
    // If no options selected, return original tree
    if (Object.keys(selectedOptions).length === 0) {
      return treeData;
    }

    return {
      ...treeData,
      nodes: filterTreeByAnswers(treeData.nodes, selectedOptions),
    };
  }, [treeData, selectedOptions]);

  const { nodes, edges } = useMemo(() => {
    if (!filteredTreeData) {
      return { nodes: [], edges: [] };
    }
    try {
      return transformTreeToFlow(filteredTreeData, handleNodeClick);
    } catch (error) {
      console.error('Error transforming tree to flow:', error);
      return { nodes: [], edges: [] };
    }
  }, [filteredTreeData, handleNodeClick]);

  // Count visible leaf nodes for roadmap creation check
  const visibleLeafCount = useMemo(() => {
    if (!filteredTreeData) return 0;
    
    const countLeaves = (nodes: TreeNode[]): number => {
      return nodes.reduce((count, node) => {
        if (node.is_leaf) {
          return count + 1;
        }
        return count + countLeaves(node.children);
      }, 0);
    };
    
    return countLeaves(filteredTreeData.nodes);
  }, [filteredTreeData]);

  // Check if roadmap can be created
  const canCreateRoadmap = useMemo(() => {
    return visibleLeafCount > 0 && visibleLeafCount <= 3;
  }, [visibleLeafCount]);

  // Handlers
  const handleOptionSelect = useCallback((questionId: string, optionId: "true" | "false") => {
    setSelectedOptions((prev) => {
      const newOptions = { ...prev, [questionId]: optionId === "true" };
      
      // If answering "false", we don't need to clear children since they won't be visible
      // If answering "true", children will become visible
      return newOptions;
    });
  }, []);

  const handlePrevQuestion = useCallback(() => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex((prev) => prev - 1);
    }
  }, [currentQuestionIndex]);

  const handleNextQuestion = useCallback(() => {
    if (currentQuestionIndex < visibleQuestions.length - 1) {
      setCurrentQuestionIndex((prev) => prev + 1);
    }
  }, [currentQuestionIndex, visibleQuestions.length]);

  // Reset question index if it's out of bounds
  useEffect(() => {
    if (currentQuestionIndex >= visibleQuestions.length && visibleQuestions.length > 0) {
      setCurrentQuestionIndex(visibleQuestions.length - 1);
    }
  }, [visibleQuestions.length, currentQuestionIndex]);

  const handleCreateRoadmap = useCallback(async () => {
    if (!filteredTreeData || !canCreateRoadmap) {
      return;
    }

    /*
    
    // Collect all leaf nodes from the filtered tree
    const targetJobs = collectLeafNodes(filteredTreeData.nodes);
    
    
    // Get topic_field IDs from leaf nodes
    const topicFieldIds = targetJobs
      .filter(job => job.topic_field)
      .map(job => job.topic_field!.id);
      
    
    if (topicFieldIds.length > 0) {
      // TODO: Get token from auth context or localStorage
      const token = localStorage.getItem('auth_token') || '';
      if (!token) {
        console.error('No authentication token found');
        // Redirect to login or show error
        return;
      }
      
      try {
        await generateRoadmap(topicFieldIds, token);
        navigate('/roadmap');
      } catch (error) {
        console.error('Failed to generate roadmap:', error);
        // Show error to user
      }
    }
      */
  }, [filteredTreeData, canCreateRoadmap, generateRoadmap, navigate]);

  return (
    <Layout>
      {/* Mobile Layout - Tree as background, Questions as overlay */}
      <div className="lg:hidden fixed inset-0 flex flex-col">
        {/* Tree - Full background */}
        <div className="flex-1 relative">
          <CareerTree nodes={nodes} edges={edges} />
        </div>

        <div className="absolute top-0 right-0 m-4 z-20 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-200 dark:border-gray-800">
          <Button
              size="lg"
              disabled={!canCreateRoadmap}
              onClick={handleCreateRoadmap}
              rightIcon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              }
            >
              Roadmap erstellen
            </Button>
        </div>

        {/* Filter Questions - Overlay at bottom */}
        <div className="absolute bottom-0 left-0 right-0 p-4 z-20">
          <div className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700">
            <FilterQuestions
              questions={visibleQuestions}
              currentQuestionIndex={currentQuestionIndex}
              selectedOptions={selectedOptions}
              onOptionSelect={handleOptionSelect}
              onPrev={handlePrevQuestion}
              onNext={handleNextQuestion}
              canGoPrev={currentQuestionIndex > 0}
              canGoNext={currentQuestionIndex < visibleQuestions.length - 1}
            />
          </div>
        </div>
      </div>

      {/* Desktop Layout - Tree as full background with overlay content */}
      <div className="hidden lg:block fixed inset-0">
        {/* Tree - Full background */}
        <div className="absolute inset-0">
          <CareerTree nodes={nodes} edges={edges} />
        </div>

        {/* Content Overlay */}
        <div className="relative z-10 h-full pointer-events-none">
          <div className="container mx-auto max-w-7xl px-6 py-8 h-full flex flex-col">
            {/* Header - Top left */}
            <div className="pointer-events-auto mb-6 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-800 px-6 py-4 max-w-2xl">
                <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-2">
                  Finde deinen{' '}
                  <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                    Karriereweg
                  </span>
                </h1>
                <p className="text-gray-600 dark:text-gray-400 text-lg">
                  Beantworte die Fragen und entdecke passende Berufsfelder.
                </p>
            </div>

            {/* Filter Questions and Indigo div - Side by side */}
            <div className="flex-1 mb-24 min-h-0 flex flex-row gap-4">
              {/* Filter Questions */}
              <div className="pointer-events-auto max-w-sm flex flex-col">
                <div className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 flex-1 flex flex-col overflow-hidden">
                  <FilterQuestions
                    questions={visibleQuestions}
                    currentQuestionIndex={currentQuestionIndex}
                    selectedOptions={selectedOptions}
                    onOptionSelect={handleOptionSelect}
                    onPrev={handlePrevQuestion}
                    onNext={handleNextQuestion}
                    canGoPrev={currentQuestionIndex > 0}
                    canGoNext={currentQuestionIndex < visibleQuestions.length - 1}
                  />
                </div>
              </div>
              
              {/* Chat Card */}
              {popupContent && (
                <div className="pointer-events-auto flex-1">
                  <Card variant="glass" className="h-full flex flex-col p-6">
                    {popupContent.topicFieldId && token ? (
                      <ChatContainer
                        topicFieldId={popupContent.topicFieldId}
                        topicFieldName={popupContent.title}
                        topicFieldDescription={popupContent.description}
                        token={token}
                        onClose={() => setPopupContent(null)}
                      />
                    ) : (
                      <>
                        <div className="flex justify-between items-start gap-4 mb-4">
                          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                            {popupContent.title}
                          </h2>
                          <button
                            onClick={() => setPopupContent(null)}
                            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 flex-shrink-0"
                          >
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              className="h-6 w-6"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M6 18L18 6M6 6l12 12"
                              />
                            </svg>
                          </button>
                        </div>
                        <p className="text-gray-600 dark:text-gray-300">
                          {popupContent.description}
                        </p>
                        {!popupContent.topicFieldId && (
                          <p className="mt-4 text-sm text-amber-600 dark:text-amber-400">
                            Chat ist nur für Leaf-Nodes mit Topic Fields verfügbar.
                          </p>
                        )}
                        {!token && (
                          <p className="mt-4 text-sm text-amber-600 dark:text-amber-400">
                            Bitte melde dich an, um den Chat zu nutzen.
                          </p>
                        )}
                      </>
                    )}
                  </Card>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Create Roadmap Button */}
      <div className="hidden lg:block fixed bottom-0 left-0 right-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-t border-gray-200 dark:border-gray-800 z-50">
        <div className="container mx-auto max-w-6xl px-4 py-4">
          <div className="flex items-center justify-end sm:justify-between">
            <div className="flex-1 hidden sm:block">
              {!canCreateRoadmap ? (
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  <span className="font-medium text-amber-600 dark:text-amber-400">
                    Hinweis:
                  </span>{' '}
                  Wähle mindestens einen Job aus oder filtere auf max. 3 Jobs.
                </p>
              ) : (
                <p className="text-sm text-green-600 dark:text-green-400">
                  ✓ Du kannst jetzt deine Roadmap erstellen!
                </p>
              )}
            </div>
            <Button
              size="lg"
              disabled={!canCreateRoadmap}
              onClick={handleCreateRoadmap}
              rightIcon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              }
            >
              Roadmap erstellen
            </Button>
          </div>
        </div>
      </div>
    </Layout>
  )
};

// ...existing code...
export default SelectionView;
