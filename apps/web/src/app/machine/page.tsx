import { Suspense } from "react";
import { MachineView } from "./machine-view";

export const metadata = { title: "Machine record" };

export default function MachinePage() {
  return (
    <div className="pt-8">
      <Suspense fallback={<p className="text-fg-muted">Loading…</p>}>
        <MachineView />
      </Suspense>
    </div>
  );
}
