import React, { useEffect, useCallback, useState, useMemo } from 'react';
import { ReactFlow, Background, Controls, getStraightPath, BaseEdge, Handle, Position, type Node, type Edge } from '@xyflow/react';
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
        hover:scale-[1.02] hover:shadow-xl hover:z-10
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
  nodes?: Node[];
  edges?: Edge[];
}

export default function CareerTree({ nodes, edges }: CareerTreeProps = {}) {
  const [isLoading, setIsLoading] = useState(true);

  const handleNodeClick = useCallback((node: TreeNode, event: React.MouseEvent) => {
    setPopupContent({
      title: node.name,
      description: node.description
    });
  }, []);

  useEffect(() => {
    if (nodes && edges) {
      setIsLoading(false);
      return;
    }
  }, [nodes, edges]);

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

  if (!nodes || nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-600 dark:text-gray-400">Kein Karrierebaum verfügbar</p>
      </div>
    );
  }

  return (
    <div style={{ height: '100%', width: '100%' }}>
      <ReactFlow nodes={nodes} edges={edges} nodeTypes={nodeTypes} fitView minZoom={0.01}/>
    </div>
  );
}