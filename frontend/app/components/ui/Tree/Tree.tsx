import React, { useEffect, useCallback, useState, useMemo } from 'react';
import { ReactFlow, Background, Controls, getStraightPath, BaseEdge, Handle, Position } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
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


interface PopupProps {
  content: { title: string; description: string } | null;
  onClose: () => void;
  position?: { x: number; y: number } | null;
}

interface TreeData {
  study_program_id: number;
  nodes: TreeNode[];
}

interface CustomNodeProps {
  data: {
    label: string;
    description?: string;
    onClick: (event: React.MouseEvent) => void;
  };
}

function CustomRoot({ data }: CustomNodeProps) {
 return (
  
    <div
      onClick={data.onClick}
      className="
        min-w-[180px]
        rounded-2xl
        bg-white/60 dark:bg-gray-800/60
        backdrop-blur-xl
        border border-white/20 dark:border-gray-700/50
        shadow-xl shadow-gray-200/30 dark:shadow-gray-900/30
        p-4
        transition-all duration-300
        hover:scale-[1.02] hover:shadow-2xl
        cursor-pointer
      "
    >
      <Handle 
        type="target" 
        position={Position.Top}
        className="!bg-white !bg-opacity-80 !border-0 !border-none !w-3 !h-3"
      />
      <div className="text-center">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
          {data.label}
        </h3>
      </div>
      <Handle 
        type="source" 
        position={Position.Bottom}
        className="!bg-white !bg-opacity-80 !border-0 !border-none !w-3 !h-3"
      />
    </div>
  );
}

function CustomLeaf({ data }: CustomNodeProps) {
  return (
    <div
      onClick={data.onClick}
      className="
        min-w-[180px]
        rounded-2xl
        bg-gradient-to-r from-indigo-600 to-purple-600
        dark:from-indigo-500 dark:to-purple-500
        shadow-lg shadow-indigo-500/25
        dark:shadow-indigo-500/20
        p-4
        transition-all duration-300
        hover:from-indigo-700 hover:to-purple-700
        dark:hover:from-indigo-600 dark:hover:to-purple-600
        hover:scale-[1.02] hover:shadow-xl
        cursor-pointer
      "
    >
      <Handle 
        type="target" 
        position={Position.Top}
        className="!bg-white !bg-opacity-80 !border-0 !border-none !w-3 !h-3"
      />
      <div className="text-center">
        <h3 className="text-sm font-semibold text-white">
          {data.label}
        </h3>
      </div>
    </div>
  );
}

const nodeTypes = {
  'custom-root': CustomRoot,
  'custom-leaf': CustomLeaf,
};

function Popup({ content, onClose }: { content: { title: string; description: string } | null; onClose: () => void }) {
  if (!content) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/50 z-40"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div 
        className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 bg-white dark:bg-gray-800 rounded-2xl shadow-2xl z-50 animate-in fade-in zoom-in duration-300"
      >
        <div className="p-6">
          <div className="flex justify-between items-start gap-4 mb-4">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">{content.title}</h2>
            <button 
              onClick={onClose} 
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 flex-shrink-0"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <p className="text-gray-600 dark:text-gray-300">{content.description}</p>
        </div>
      </div>
    </>
  );
}



function transformTreeToFlow(data: TreeData, onNodeClick: (node: TreeNode, event: React.MouseEvent) => void) {
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
      data: { label: node.name,
        description: node.description,
        onClick: (event: React.MouseEvent) => onNodeClick(node, event)
       },
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
  }, []);
  
  return { nodes, edges };
}

interface CareerTreeProps {
  studyProgramId?: number;
  token?: string;
}

export default function CareerTree({ studyProgramId = 1, token }: CareerTreeProps = {}) {
  const [treeData, setTreeData] = useState<TreeData | null>(null);
  const [popupContent, setPopupContent] = useState<{ title: string; description: string } | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchTree = async () => {
      setIsLoading(true);
      try {
        const authToken = token || localStorage.getItem('auth_token') || undefined;
        const response = await getTree(studyProgramId, authToken);
        if (response && response.nodes && Array.isArray(response.nodes)) {
          setTreeData(response);
        } else {
          console.error('Invalid tree data structure:', response);
          setTreeData(null);
        }
      } catch (error) {
        console.error('Failed to fetch tree:', error);
        setTreeData(null);
      } finally {
        setIsLoading(false);
      }
    };
    fetchTree();
  }, [studyProgramId, token]);

  const handleNodeClick = useCallback((node: TreeNode, event: React.MouseEvent) => {
    setPopupContent({
      title: node.name,
      description: node.description
    });
  }, []);
  

  const { nodes, edges } = useMemo(() => {
    if (!treeData) {
      return { nodes: [], edges: [] };
    }
    return transformTreeToFlow(treeData, handleNodeClick);
  }, [treeData, handleNodeClick]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mx-auto mb-2"></div>
          <p className="text-gray-600 dark:text-gray-400 text-sm">Lade Karrierebaum...</p>
        </div>
      </div>
    );
  }

  if (!treeData || nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-600 dark:text-gray-400">Kein Karrierebaum verfügbar</p>
      </div>
    );
  }

  return (
    <div style={{ height: '100%', width: '100%' }}>
      <ReactFlow nodes={nodes} edges={edges} nodeTypes={nodeTypes} fitView />
      <Popup content={popupContent} onClose={() => setPopupContent(null)} />
    </div>
  );
}