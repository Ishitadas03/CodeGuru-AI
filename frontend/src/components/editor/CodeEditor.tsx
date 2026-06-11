"use client";

import React from "react";
import Editor, { Monaco } from "@monaco-editor/react";
import { defaultEditorOptions, setupMonacoThemes } from "@/lib/monaco-config";

interface CodeEditorProps {
  value: string;
  onChange: (value: string | undefined) => void;
  language: string;
  readOnly?: boolean;
}

export default function CodeEditor({
  value,
  onChange,
  language,
  readOnly = false,
}: CodeEditorProps) {
  const handleEditorWillMount = (monaco: Monaco) => {
    setupMonacoThemes(monaco);
  };

  const options = {
    ...defaultEditorOptions,
    readOnly,
  };

  return (
    <div className="w-full h-full min-h-[400px] border border-aether rounded-2xl overflow-hidden shadow-2xl bg-obsidian">
      <Editor
        height="100%"
        language={language}
        value={value}
        onChange={onChange}
        theme="aetherFlow"
        options={options}
        beforeMount={handleEditorWillMount}
      />
    </div>
  );
}
