"use client";

import React from "react";
import { DiffEditor, Monaco } from "@monaco-editor/react";
import { defaultEditorOptions, setupMonacoThemes } from "@/lib/monaco-config";

interface RefactoredCodeProps {
  originalCode: string;
  refactoredCode: string;
  language: string;
}

export default function RefactoredCode({
  originalCode,
  refactoredCode,
  language,
}: RefactoredCodeProps) {
  const handleEditorWillMount = (monaco: Monaco) => {
    setupMonacoThemes(monaco);
  };

  const diffOptions = {
    ...defaultEditorOptions,
    readOnly: true,
    originalEditable: false,
    renderSideBySide: true, // Enable side-by-side diff comparison
  };

  return (
    <div className="w-full h-full min-h-[500px] border border-aether rounded-2xl overflow-hidden bg-obsidian shadow-2xl">
      <DiffEditor
        language={language}
        original={originalCode}
        modified={refactoredCode}
        theme="aetherFlow"
        options={diffOptions}
        beforeMount={handleEditorWillMount}
      />
    </div>
  );
}
