export default function ImagePlaceholder() {
  return (
    <div className="w-full h-[550px] rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 flex flex-col items-center justify-center">

      <div className="text-6xl mb-4">
        🛰️
      </div>

      <h3 className="text-xl font-semibold text-slate-700">
        No Visualization Selected
      </h3>

      <p className="mt-2 text-slate-500 text-center max-w-lg">
        Select one of the available AI visualization layers above to
        display the analysis output.
      </p>

    </div>
  );
}