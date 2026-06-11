import { Monaco } from "@monaco-editor/react";

export const aetherFlowTheme = {
  base: "vs-dark" as const,
  inherit: false,
  rules: [
    { token: "keyword",   foreground: "5B6CF9", fontStyle: "bold" },
    { token: "string",    foreground: "34D399" },
    { token: "comment",   foreground: "3D4A6B", fontStyle: "italic" },
    { token: "number",    foreground: "F472B6" },
    { token: "function",  foreground: "22D3EE" },
    { token: "variable",  foreground: "F0F4FF" },
    { token: "type",      foreground: "A855F7" },
    { token: "operator",  foreground: "9B59F5" },
    { token: "class",     foreground: "34D399", fontStyle: "bold" },
    { token: "interface", foreground: "38BDF8" },
  ],
  colors: {
    "editor.background":              "#060814",
    "editor.foreground":              "#F0F4FF",
    "editorLineNumber.foreground":    "#3D4A6B",
    "editorLineNumber.activeForeground": "#5B6CF9",
    "editor.selectionBackground":     "rgba(91,108,249,0.2)",
    "editor.lineHighlightBackground": "#0B0F20",
    "editorCursor.foreground":        "#22D3EE",
    "editorIndentGuide.background":   "#1A2040",
    "scrollbar.shadow":               "#060814",
    "editorWidget.background":        "#0B0F20",
    "editorSuggestWidget.background": "#101428",
    "editorSuggestWidget.border":     "rgba(91,108,249,0.2)",
    "editorSuggestWidget.selectedBackground": "#1A2040",
  },
};

export const defaultEditorOptions = {
  fontSize: 14,
  fontFamily: "var(--font-jetbrains), 'JetBrains Mono', Menlo, Monaco, monospace",
  minimap: { enabled: false },
  wordWrap: "on" as const,
  lineNumbers: "on" as const,
  scrollbar: {
    vertical: "visible" as const,
    horizontal: "visible" as const,
    verticalScrollbarSize: 8,
    horizontalScrollbarSize: 8,
  },
  automaticLayout: true,
  tabSize: 4,
  padding: { top: 12, bottom: 12 },
};

export function setupMonacoThemes(monaco: Monaco) {
  monaco.editor.defineTheme("aetherFlow", aetherFlowTheme);
}
