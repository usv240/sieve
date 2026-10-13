import { Suspense } from "react";
import { TryFlow } from "@/components/try-flow";

export const metadata = { title: "Try Sieve" };

export default function TryPage() {
  return (
    <div className="pt-8">
      <Suspense fallback={<p className="text-fg-muted">Loading…</p>}>
        <TryFlow />
      </Suspense>
    </div>
  );
}
