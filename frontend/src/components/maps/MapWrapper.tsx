"use client";

import dynamic from "next/dynamic";

const InteractiveMap = dynamic(
  () => import("./InteractiveMap"),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-[500px] rounded-xl border border-gray-200 bg-gray-100 flex items-center justify-center">
        <p className="text-gray-500">Loading map...</p>
      </div>
    ),
  }
);

export default function MapWrapper() {
  return <InteractiveMap />;
}