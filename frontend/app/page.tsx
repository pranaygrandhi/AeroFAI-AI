import UploadPanel from "../components/UploadPanel";

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-6xl flex-col gap-8 px-6 py-12">
      <section className="rounded-3xl border border-slate-800 bg-slate-900/80 p-10 shadow-xl shadow-slate-900/20">
        <div className="space-y-4">
          <h1 className="text-4xl font-semibold tracking-tight text-white">AeroFAI AI</h1>
          <p className="max-w-2xl text-slate-300">
            Enterprise-grade AS9102 First Article Inspection software. Upload PDF drawings, review
            auto-ballooned characteristics, and generate inspection reports with aerospace-grade
            confidence.
          </p>
        </div>
      </section>

      <UploadPanel />
    </main>
  );
}
