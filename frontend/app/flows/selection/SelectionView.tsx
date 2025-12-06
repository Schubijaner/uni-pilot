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

interface TreeNode {
  id: number;
  name: string;
  description: string;
  is_leaf: boolean;
  level: number;
  children: TreeNode[];
  topic_field?: {
    id: number;
    name: string;
    description: string;
  };
}

interface TreeData {
  study_program_id: number;
  nodes: TreeNode[]; // Nach Normalisierung durch getTree ist dies immer ein Array
}

function transformTreeToFlow(data: TreeData | null) {
  const nodes: any[] = [];
  const edges: any[] = [];
  
  // Safety check: return empty if data is invalid
  if (!data || !data.nodes || !Array.isArray(data.nodes)) {
    return { nodes, edges };
  }
  
  const processNode = (node: TreeNode, parentId: string | null, xOffset: number, siblingIndex: number, siblingCount: number) => {
    const nodeId = `n${node.id}`;
    const xSpacing = 250;
    const ySpacing = 150;
    
    // Calculate x position based on sibling index
    const x = xOffset + (siblingIndex - (siblingCount - 1) / 2) * xSpacing;
    const y = (node.level - 1) * ySpacing;
    
    nodes.push({
      id: nodeId,
      position: { x, y },
      data: { label: node.name },
      type: node.is_leaf ? "custom-leaf" : "custom-root",
    });
    
    if (parentId) {
      edges.push({
        id: `${parentId}-${nodeId}`,
        source: parentId,
        target: nodeId,
        style: { stroke: '#6366f1', strokeWidth: 2 } // Custom color here
      });
    }
    
    // Process children - add safety check
    if (node.children && Array.isArray(node.children)) {
      node.children.forEach((child, index) => {
        processNode(child, nodeId, x, index, node.children.length);
      });
    }
  };
  
  // Process root nodes
  data.nodes.forEach((node, index) => {
    const rootSpacing = 600;
    const xOffset = index * rootSpacing;
    processNode(node, null, xOffset, 0, 1);
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
  
  // For now, return all nodes since TreeNode doesn't have questions property
  // TODO: Add questions to TreeNode interface or filter based on topic_field
  return nodes.map((node) => {
    // Recursively filter children - add safety check
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

export const SelectionView: React.FC = () => {
  const navigate = useNavigate();
  const { state, toggleJob, generateRoadmap } = useApp();
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedOptions, setSelectedOptions] = useState<Record<string, boolean>>({});
  const [questions, setQuestions] = useState<UserQuestion[]>([]);
  const [isLoadingTree, setIsLoadingTree] = useState(true);
  const [isLoadingQuestions, setIsLoadingQuestions] = useState(true);
  const [treeError, setTreeError] = useState<string | null>(null);

  const [treeData, setTreeData] = useState<TreeData | null>(null);

  useEffect(() => {
    const loadQuestions = async () => {
      setIsLoadingQuestions(true);
      const token = localStorage.getItem('auth_token') || '';
      if (token) {
        try {
          const fetchQuestions = await getUserQuestions(token);
          setQuestions(fetchQuestions.items || []);
        } catch (error) {
          console.error('Failed to load user questions:', error);
          setQuestions([]);
        } finally {
          setIsLoadingQuestions(false);
        }
      } else {
        setIsLoadingQuestions(false);
      }
    };
    const fetchTree = async () => {
      setIsLoadingTree(true);
      setTreeError(null);
      try {
        // TODO: Get study program ID from user profile or context
        const studyProgramId = 1; // This should come from user profile
        const token = localStorage.getItem('auth_token') || undefined;
        const response = await getTree(studyProgramId, token);
        // Validate response structure
        if (response && response.nodes && Array.isArray(response.nodes)) {
          setTreeData(response);
        } else {
          console.error('Invalid tree data structure:', response);
          setTreeData(null);
          setTreeError('Ungültige Datenstruktur vom Server');
        }
      } catch (error) {
        console.error('Failed to fetch tree:', error);
        setTreeData(null);
        setTreeError('Fehler beim Laden des Karrierebaums');
      } finally {
        setIsLoadingTree(false);
      }
    };
    fetchTree();
    loadQuestions();
  }, []);

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
      return transformTreeToFlow(filteredTreeData);
    } catch (error) {
      console.error('Error transforming tree to flow:', error);
      return { nodes: [], edges: [] };
    }
  }, [filteredTreeData]);

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
    setSelectedOptions((prev) => ({ ...prev, [questionId]: optionId === "true" ? true : false }));
  }, []);

  const handlePrevQuestion = useCallback(() => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex((prev) => prev - 1);
    }
  }, [currentQuestionIndex]);

  const handleNextQuestion = useCallback(() => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex((prev) => prev + 1);
    }
  }, [currentQuestionIndex, questions.length]);

  const handleCreateRoadmap = useCallback(async () => {
    if (!filteredTreeData || !canCreateRoadmap) {
      return;
    }
    
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
  }, [filteredTreeData, canCreateRoadmap, generateRoadmap, navigate]);

  return (
    <Layout>
      {/* Header */}
      <div className="mb-8">
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

      {/* Main Content */}
      {isLoadingTree || isLoadingQuestions ? (
        <div className="flex items-center justify-center py-16">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Lade Daten...</p>
          </div>
        </div>
      ) : treeError ? (
        <div className="flex items-center justify-center py-16">
          <Card variant="glass" className="max-w-md">
            <div className="text-center py-8">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Fehler beim Laden
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">{treeError}</p>
              <Button onClick={() => window.location.reload()}>
                Seite neu laden
              </Button>
            </div>
          </Card>
        </div>
      ) : !treeData || nodes.length === 0 ? (
        <div className="flex items-center justify-center py-16">
          <Card variant="glass" className="max-w-md">
            <div className="text-center py-8">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
                <svg className="w-8 h-8 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Keine Daten verfügbar
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Der Karrierebaum konnte nicht geladen werden. Bitte versuche es später erneut.
              </p>
            </div>
          </Card>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Filter Questions (Left on Desktop, Bottom on Mobile) */}
          <div className="order-2 lg:order-1">
            {questions.length > 0 ? (
              <FilterQuestions
                questions={questions}
                currentQuestionIndex={currentQuestionIndex}
                selectedOptions={selectedOptions}
                onOptionSelect={handleOptionSelect}
                onPrev={handlePrevQuestion}
                onNext={handleNextQuestion}
                canGoPrev={currentQuestionIndex > 0}
                canGoNext={currentQuestionIndex < questions.length - 1}
              />
            ) : (
              <Card variant="glass">
                <div className="text-center py-8">
                  <p className="text-gray-600 dark:text-gray-400">
                    Keine Fragen verfügbar
                  </p>
                </div>
              </Card>
            )}
          </div>

          {/* Job Tree (Right on Desktop, Top on Mobile) */}
          <div className="order-1 lg:order-2 lg:col-span-2" style={{ height: '600px' }}>
            {treeData && treeData.nodes && treeData.nodes.length > 0 ? (
              <div style={{ height: '100%', width: '100%' }}>
                <CareerTree studyProgramId={treeData.study_program_id} />
              </div>
            ) : (
              <Card variant="glass">
                <div className="text-center py-8">
                  <p className="text-gray-600 dark:text-gray-400">
                    Kein Karrierebaum verfügbar
                  </p>
                </div>
              </Card>
            )}
          </div>
        </div>
      )}

      {/* Create Roadmap Button */}
      <div className="fixed bottom-0 left-0 right-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-t border-gray-200 dark:border-gray-800 z-50">
        <div className="container mx-auto max-w-6xl px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex-1">
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

      {/* Spacer for fixed bottom bar */}
      <div className="h-24" />
    </Layout>
  );
};

export default SelectionView;
