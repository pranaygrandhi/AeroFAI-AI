import UploadPanel from "../components/UploadPanel";

const stats = [
  { label: "Active drawings", value: "8", detail: "This week" },
  { label: "Ballooned features", value: "24", detail: "Auto-extracted" },
  { label: "Average confidence", value: "98.3%", detail: "Latest analysis" },
];

const tasks = [
  "Upload a PDF drawing",
  "Review automatic feature balloons",
  "Export AS9102 and inspection reports",
];

const features = [
  {
    title: "PDF Drawing Viewer",
    description: "Open engineering drawing PDFs directly in the browser with page navigation, zoom, and pan.",
    href: "#upload",
  },
  {
    title: "Manual Ballooning",
    description: "Place, move, and renumber balloon callouts with precision, including leader line placement.",
    href: "#results",
  },
  {
    title: "Feature Table",
    description: "Build an editable characteristic table with nominal, tolerance, type, and comments.",
    href: "#results",
  },
  {
    title: "AS9102 Form 3 Export",
    description: "Export your characteristic data to Excel or CSV for AS9102 Form 3 submission.",
    href: "#results",
  },
  {
    title: "Google Drive Save/Load",
    description: "Save and reload your project from Google Drive, including drawing, balloons, and table.",
    href: "#drive",
  },
  {
    title: "OCR Assisted Extraction",
    description: "Beta automatic dimension and tolerance extraction from drawing text.",
    badge: "Beta",
    href: "#upload",
  },
];

export default function Home() {
  return (
    <main className="relative overflow-hidden bg-slate-950 text-slate-100">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-80 bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.14),transparent_34%)]" />
      <div className="mx-auto flex min-h-screen max-w-[1480px] flex-col gap-8 px-4 py-6 sm:px-6 lg:px-8">
        <header className="relative z-10 flex flex-col gap-6 rounded-[2rem] border border-slate-800/80 bg-slate-950/90 p-6 shadow-[0_40px_120px_-80px_rgba(15,23,42,0.9)] sm:p-8">
          <nav className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-cyan-300">AeroFAI</p>
              <h1 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">A smarter inspection workspace for aerospace drawings</h1>
            </div>
            <div className="flex flex-wrap items-center gap-3 text-sm text-slate-300">
              <a href="#upload" className="rounded-full border border-slate-700 bg-slate-900/90 px-4 py-2 transition hover:border-cyan-400 hover:text-white">Upload</a>
              <a href="#results" className="rounded-full border border-slate-700 bg-slate-900/90 px-4 py-2 transition hover:border-cyan-400 hover:text-white">Results</a>
              <a href="#status" className="rounded-full border border-slate-700 bg-slate-900/90 px-4 py-2 transition hover:border-cyan-400 hover:text-white">Status</a>
            </div>
          </nav>

          <section className="grid gap-8 xl:grid-cols-[1.4fr_0.9fr] xl:items-end">
            <div className="space-y-6">
              <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">Inspection dashboard</p>
              <div className="space-y-4">
                <h2 className="text-4xl font-semibold tracking-tight text-white sm:text-5xl">
                  Intelligent FAI inspection for aerospace drawings and reports.
                </h2>
                <p className="max-w-3xl text-base leading-8 text-slate-400 sm:text-lg">
                  Upload drawings, auto-generate balloons, review features, and export inspection reports from a polished, web-first workflow.
                </p>
              </div>
              <div className="flex flex-wrap gap-3 text-sm text-slate-300">
                <span className="rounded-full bg-slate-800/80 px-4 py-2">Secure uploads</span>
                <span className="rounded-full bg-slate-800/80 px-4 py-2">Live status tracking</span>
                <span className="rounded-full bg-slate-800/80 px-4 py-2">AS9102 ready</span>
              </div>
            </div>

            <aside className="grid gap-4 sm:grid-cols-2 xl:grid-cols-1">
              {stats.map((item) => (
                <article key={item.label} className="rounded-[1.6rem] border border-slate-800/80 bg-slate-900/90 p-5 shadow-sm shadow-slate-950/20">
                  <p className="text-sm uppercase tracking-[0.28em] text-slate-500">{item.label}</p>
                  <p className="mt-4 text-3xl font-semibold text-white">{item.value}</p>
                  <p className="mt-2 text-sm text-slate-400">{item.detail}</p>
                </article>
              ))}
            </aside>
          </section>

          <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature) => (
              <a
                key={feature.title}
                href={feature.href}
                className="group rounded-[1.8rem] border border-slate-800/80 bg-slate-900/90 p-5 shadow-sm shadow-slate-950/20 transition hover:-translate-y-1 hover:border-cyan-400/40"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-cyan-500/10 text-cyan-300">•</div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">{feature.title}</h3>
                    {feature.badge ? (
                      <span className="mt-1 inline-flex rounded-full bg-amber-500/10 px-3 py-1 text-[11px] uppercase tracking-[0.3em] text-amber-300">{feature.badge}</span>
                    ) : null}
                  </div>
                </div>
                <p className="mt-4 text-sm leading-6 text-slate-400">{feature.description}</p>
              </a>
            ))}
          </section>
        </header>

        <section id="upload" className="grid gap-6 xl:grid-cols-[1.3fr_0.7fr]">
          <article className="space-y-6 rounded-[2rem] border border-slate-800/80 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="text-sm uppercase tracking-[0.24em] text-cyan-300">Upload workspace</p>
                <h2 className="mt-2 text-2xl font-semibold text-white">Ready for your next drawing</h2>
              </div>
              <span className="rounded-full bg-slate-800/80 px-4 py-2 text-xs uppercase tracking-[0.28em] text-slate-300">
                Realtime processing
              </span>
            </div>

            <UploadPanel />
          </article>

          <aside className="space-y-6">
            <section id="status" className="rounded-[2rem] border border-slate-800/80 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20">
              <p className="text-sm uppercase tracking-[0.24em] text-slate-500">Quick actions</p>
              <ul className="mt-6 space-y-3">
                {tasks.map((task) => (
                  <li key={task} className="flex items-start gap-3 rounded-[1.6rem] border border-slate-800 bg-slate-950/80 p-4">
                    <span className="mt-1 inline-flex h-3 w-3 rounded-full bg-cyan-400" />
                    <p className="text-sm leading-6 text-slate-200">{task}</p>
                  </li>
                ))}
              </ul>
            </section>

            <section className="rounded-[2rem] border border-slate-800/80 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20">
              <div className="flex items-center justify-between">
                <p className="text-sm uppercase tracking-[0.24em] text-slate-500">Inspection status</p>
                <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-emerald-300">
                  Online
                </span>
              </div>
              <div className="mt-6 space-y-4">
                <div className="rounded-[1.6rem] bg-slate-950/80 p-4">
                  <p className="text-sm text-slate-400">Current job</p>
                  <p className="mt-2 text-lg font-semibold text-white">Aero panel revision A</p>
                </div>
                <div className="rounded-[1.6rem] bg-slate-950/80 p-4">
                  <p className="text-sm text-slate-400">Next step</p>
                  <p className="mt-2 text-lg font-semibold text-white">Export AS9102 package</p>
                </div>
              </div>
            </section>
          </aside>
        </section>

        <section id="drive" className="rounded-[2rem] border border-slate-800/80 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.24em] text-cyan-300">Google Drive</p>
              <h2 className="mt-2 text-2xl font-semibold text-white">Save and reload your project</h2>
            </div>
            <div className="flex flex-wrap gap-3">
              <button className="rounded-full border border-slate-700 bg-slate-950/90 px-4 py-2 text-sm text-white transition hover:border-cyan-400" type="button">
                Connect Drive
              </button>
              <button className="rounded-full border border-slate-700 bg-slate-950/90 px-4 py-2 text-sm text-white transition hover:border-cyan-400" type="button">
                Save project
              </button>
              <button className="rounded-full border border-slate-700 bg-slate-950/90 px-4 py-2 text-sm text-white transition hover:border-cyan-400" type="button">
                Load project
              </button>
            </div>
          </div>
          <p className="mt-5 max-w-3xl text-sm leading-7 text-slate-400">
            Store your drawing, balloon positions, and feature table on Google Drive for easy reuse and collaboration.
          </p>
        </section>
      </div>
    </main>
  );
}
