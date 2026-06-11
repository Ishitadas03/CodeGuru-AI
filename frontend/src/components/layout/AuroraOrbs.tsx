// src/components/layout/AuroraOrbs.tsx

export default function AuroraOrbs() {
  return (
    <div 
      className="fixed inset-0 overflow-hidden pointer-events-none"
      style={{ zIndex: 1 }}
    >
      {/* Top-left — indigo pool */}
      <div style={{
        position: 'absolute', top: '-15%', left: '-10%',
        width: '55vw', height: '55vw', borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(91,108,249,0.12) 0%, transparent 70%)',
        animation: 'orb-drift-1 18s ease-in-out infinite',
      }}/>
      
      {/* Top-right — violet bloom */}
      <div style={{
        position: 'absolute', top: '-5%', right: '-15%',
        width: '45vw', height: '45vw', borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(155,89,245,0.1) 0%, transparent 70%)',
        animation: 'orb-drift-2 22s ease-in-out infinite',
      }}/>
      
      {/* Bottom-center — teal rise */}
      <div style={{
        position: 'absolute', bottom: '-10%', left: '30%',
        width: '50vw', height: '40vw', borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(34,211,238,0.08) 0%, transparent 70%)',
        animation: 'orb-drift-3 26s ease-in-out infinite',
      }}/>
      
      {/* Center — purple ambient */}
      <div style={{
        position: 'absolute', top: '40%', left: '50%',
        transform: 'translate(-50%,-50%)',
        width: '60vw', height: '30vw', borderRadius: '50%',
        background: 'radial-gradient(ellipse, rgba(168,85,247,0.06) 0%, transparent 65%)',
        animation: 'orb-drift-1 30s ease-in-out infinite reverse',
      }}/>
    </div>
  )
}
