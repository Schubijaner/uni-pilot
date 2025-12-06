/**
 * SelectionView - Hauptansicht für die Job-Auswahl
 * Kombiniert Job-Tree und Filter-Fragen
 */

import React, { useState, useMemo, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router';
import { Layout } from '~/components/layout';
import { Button, Card } from '~/components/ui';
import { useApp } from '~/contexts';
import { JOB_BRANCHES, FILTER_QUESTIONS } from '~/data/mockData';
import { JobTree } from './components/JobTree';
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
  nodes: TreeNode[];
}

function transformTreeToFlow(data: TreeData) {
  const nodes: any[] = [];
  const edges: any[] = [];
  
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
    
    // Process children
    node.children.forEach((child, index) => {
      processNode(child, nodeId, x, index, node.children.length);
    });
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
  nodes: TreeNode[],
  selectedOptions: Record<string, boolean>
): TreeNode[] {
  return nodes
    .map((node) => {
      // Check if this node's questions match user answers
      const nodeMatches = !node.questions || node.questions.every((q) => {
        const questionId = String(q.id);
        // If user hasn't answered this question, don't filter it out
        if (!(questionId in selectedOptions)) {
          return true;
        }
        // Check if user's answer matches the expected answer
        return selectedOptions[questionId] === q.answer;
      });

      // If node doesn't match, exclude it entirely
      if (!nodeMatches) {
        return null;
      }

      // Recursively filter children
      const filteredChildren = filterTreeByAnswers(node.children, selectedOptions);

      // Return node with filtered children
      return {
        ...node,
        children: filteredChildren,
      };
    })
    .filter((node): node is TreeNode => node !== null);
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

  const [treeData, setTreeData] = useState<TreeData | null>(null);

  useEffect(() => {
    const loadQuestions = async () => {
      const fetchQuestions = await getUserQuestions('your-auth-token-here');
      setQuestions(fetchQuestions.items);
    };
    const fetchTree = async () => {
      const response = await getTree('mock-token', 1);
      setTreeData(response);
    };
    fetchTree();
    loadQuestions();
  }, []);

  // Filter the tree based on user's answers
  const filteredTreeData = useMemo(() => {
    if (!treeData) {
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
    return transformTreeToFlow(filteredTreeData);
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

  const handleCreateRoadmap = useCallback(() => {
    if (!filteredTreeData || !canCreateRoadmap) {
      return;
    }
    
    // Collect all leaf nodes from the filtered tree
    const targetJobs = collectLeafNodes(filteredTreeData.nodes);
    
    // Get topic_field IDs if you need those instead
    const topicFieldIds = targetJobs
      .filter(job => job.topic_field)
      .map(job => job.topic_field!.id);
    
    // Or just the node IDs
    const targetJobIds = targetJobs.map(job => job.id);
    
    if (targetJobIds.length > 0) {
      // Pass all IDs if generateRoadmap supports an array
      generateRoadmap(targetJobIds);
      navigate('/roadmap');
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
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Filter Questions (Left on Desktop, Bottom on Mobile) */}
        <div className="order-2 lg:order-1">
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
        </div>

        {/* Job Tree (Right on Desktop, Top on Mobile) */}
        <div className="order-1 lg:order-2 lg:col-span-2">
          <CareerTree nodes={nodes} edges={edges}/>
          {/*<Card variant="glass" padding="md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Verfügbare Berufe
              </h2>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {visibleJobs.length} sichtbar
                </span>
                {state.selectedJobs.length > 0 && (
                  <span className="px-2.5 py-0.5 text-xs font-medium rounded-full bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400">
                    {state.selectedJobs.length} ausgewählt
                  </span>
                )}
              </div>
            </div>

            <JobTree
              branches={JOB_BRANCHES}
              visibleJobs={visibleJobs}
              selectedJobs={state.selectedJobs}
              onJobToggle={toggleJob}
            />
          </Card>*/}
        </div>
      </div>

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
