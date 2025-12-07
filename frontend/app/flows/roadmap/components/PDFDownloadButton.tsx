import React, { useState, useEffect } from 'react';
import { Button } from '~/components/ui';
import type { CareerPath, Skill } from '~/types';

interface PDFDownloadButtonProps {
  careerPath: CareerPath;
  userSkills: Skill[];
}

/**
 * Client-side only PDF download button
 * Dynamically imports @react-pdf/renderer to avoid SSR issues
 */
const PDFDownloadButton: React.FC<PDFDownloadButtonProps> = ({ careerPath, userSkills }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const handleDownload = async () => {
    if (!isClient) return;
    
    setIsGenerating(true);
    
    try {
      // Dynamically import react-pdf to avoid SSR issues
      const [{ pdf }, { RoadmapPDF }] = await Promise.all([
        import('@react-pdf/renderer'),
        import('./RoadmapPDF'),
      ]);

      const blob = await pdf(
        <RoadmapPDF careerPath={careerPath} userSkills={userSkills} />
      ).toBlob();

      // Create download link
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `roadmap-${careerPath.jobName.toLowerCase().replace(/\s+/g, '-')}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('PDF generation failed:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  if (!isClient) {
    return (
      <Button disabled>
        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
        PDF Export
      </Button>
    );
  }

  return (
    <Button onClick={handleDownload} disabled={isGenerating}>
      {isGenerating ? (
        <>
          <svg className="w-5 h-5 mr-2 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          Wird erstellt...
        </>
      ) : (
        <>
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          PDF Export
        </>
      )}
    </Button>
  );
};

export default PDFDownloadButton;
