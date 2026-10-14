/** Downscale a photo in the browser before upload. Hosted APIs cap request bodies (Vercel: 4.5 MB); a phone photo is often 3 to 8 MB. */
export async function downscaleImage(file: File, maxDim = 1600, quality = 0.85): Promise<Blob> {
  if (file.size < 1_200_000) return file;
  try {
    const bitmap = await createImageBitmap(file);
    const scale = Math.min(1, maxDim / Math.max(bitmap.width, bitmap.height));
    const w = Math.round(bitmap.width * scale), h = Math.round(bitmap.height * scale);
    const canvas = document.createElement("canvas"); canvas.width = w; canvas.height = h;
    const ctx = canvas.getContext("2d"); if (!ctx) return file;
    ctx.drawImage(bitmap, 0, 0, w, h);
    const blob = await new Promise<Blob | null>((res) => canvas.toBlob(res, "image/jpeg", quality));
    return blob && blob.size < file.size ? blob : file;
  } catch { return file; }
}

export const UPLOAD_LIMIT_BYTES = 4_300_000;
export const UPLOAD_LIMIT_NOTE = "That file is over 4 MB, the hosted demo's request limit. Run the API locally (make dev) for larger files.";
