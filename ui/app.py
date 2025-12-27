import time
import threading
import customtkinter as ctk
from tkinter import messagebox
from core.analyzer import seo_score, niche_opportunity_score, MAX_RESULTS, AVG_TIME_PER_VIDEO_SEC
from core.youtube_api import search_youtube_detailed



class YouTubeAnalyzerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Niche Analyzer")
        self.geometry("700x500")
        self.resizable(False, False)
        self.configure(fg_color="#2b2b2b")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.show_input()

    def show_input(self):
        self.input_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.input_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.input_frame.grid_rowconfigure((0, 1, 2), weight=1)
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(
            self.input_frame,
            text="Enter search query:",
            font=("Arial", 16),
            text_color="#FFFFFF"
        )
        self.label.grid(row=0, column=0, pady=(20, 10), sticky="n")

        self.query_entry = ctk.CTkEntry(
            self.input_frame,
            width=400,
            fg_color="#3a3a3a",
            text_color="#FFFFFF",
            placeholder_text_color="#AAAAAA",
            border_color="#FF8C00"
        )
        self.query_entry.grid(row=1, column=0, pady=(0, 20), sticky="n")

        self.start_button = ctk.CTkButton(
            self.input_frame,
            text="Analyze",
            command=self.start_analysis,
            fg_color="#FF8C00",
            hover_color="#CC6A00",
            text_color="#000000"
        )
        self.start_button.grid(row=2, column=0, pady=(0, 20), sticky="n")

    def start_analysis(self):
        query = self.query_entry.get().strip()
        if not query:
            messagebox.showerror("Invalid input", "Please enter a search query to analyze.")
            return
        self.input_frame.grid_forget()
        self._cancel_requested = False
        self.start_button.configure(state="disabled")
        # add cancel button
        self.cancel_button = ctk.CTkButton(
            self.input_frame,
            text="Cancel",
            command=self.request_cancel,
            fg_color="#555555",
            hover_color="#444444",
            text_color="#FFFFFF"
        )
        # keep hidden until needed

        self.progress_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.progress_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.progress_frame.grid_rowconfigure((0, 1), weight=1)
        self.progress_frame.grid_columnconfigure(0, weight=1)

        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text=f"Analyzing '{query}'...\nEstimated time: ~{AVG_TIME_PER_VIDEO_SEC * MAX_RESULTS:.0f} seconds",
            font=("Arial", 14),
            text_color="#FFFFFF"
        )
        self.progress_label.grid(row=0, column=0, pady=(30, 20), sticky="n")

        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            mode="indeterminate",
            progress_color="#FF8C00",
            fg_color="#3a3a3a"
        )
        self.progress_bar.grid(row=1, column=0, padx=50, pady=(0, 30), sticky="ew")
        self.progress_bar.start()

        threading.Thread(target=self.run_analysis, args=(query,), daemon=True).start()

    def request_cancel(self):
        self._cancel_requested = True

    def run_analysis(self, query):
        start_time = time.time()
        try:
            videos = search_youtube_detailed(query, max_results=MAX_RESULTS, last_week_only=True)
            if self._cancel_requested:
                raise RuntimeError("Canceled by user")
            valid_videos = []
            for v in videos:
                required = ["views", "likes", "comments", "duration", "date"]
                if all(v.get(k) is not None for k in required) and v["duration"] > 0 and v["views"] is not None:
                    valid_videos.append(v)

            if not valid_videos:
                result_text = "❌ No videos with sufficient data for analysis."
            else:
                seo_scores = []
                durations_sec = []
                views_list = []

                for v in valid_videos:
                    if self._cancel_requested:
                        raise RuntimeError("Canceled by user")
                    # update per-video progress
                    idx = len(seo_scores) + 1
                    self.after(0, lambda i=idx, total=len(valid_videos): self.progress_label.configure(text=f"Analyzing '{query}' — video {i}/{total}"))
                    subs = v.get("followers", 1000)
                    score = seo_score(v, subs)
                    if score is not None:
                        seo_scores.append(score)
                    durations_sec.append(v["duration"])
                    views_list.append(v["views"])

                avg_seo = sum(seo_scores) / len(seo_scores) if seo_scores else 0
                avg_duration_sec = sum(durations_sec) / len(durations_sec)
                avg_views = sum(views_list) / len(views_list)

                opportunity = niche_opportunity_score(avg_seo, avg_views, avg_duration_sec)

                verdict = ""
                if opportunity > 70:
                    verdict = "Excellent niche for publishing!"
                elif opportunity > 50:
                    verdict = "Moderate potential. High-quality content required."
                else:
                    verdict = "Low engagement. Risk of poor reach."

                result_text = (
                    f"📊 Analysis for query '{query}':\n\n"
                    f"• Avg SEO score: {avg_seo:.2f}/100\n"
                    f"• Avg duration: {avg_duration_sec / 60:.1f} min\n"
                    f"• Avg views: {avg_views:.0f}\n\n"
                    f"🎯 Niche opportunity score: {opportunity:.1f}/100\n"
                    f"{verdict}"
                )
        except Exception as e:
            result_text = f"⚠️ Error during analysis:\n{str(e)}"

        elapsed = time.time() - start_time
        final_text = f"{result_text}\n\n⏱️ Execution time: {elapsed:.1f} sec."

        self.after(0, self.show_result, final_text)

    def show_result(self, result_text):
        self.progress_bar.stop()
        self.progress_frame.grid_forget()
        # re-enable start button for new analyses
        try:
            self.start_button.configure(state="normal")
        except Exception:
            pass

        self.result_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.result_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.result_frame.grid_rowconfigure(0, weight=1)
        self.result_frame.grid_columnconfigure(0, weight=1)

        self.result_textbox = ctk.CTkTextbox(
            self.result_frame,
            wrap="word",
            font=("Consolas", 13),
            fg_color="#3a3a3a",
            text_color="#FFFFFF"
        )
        self.result_textbox.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.result_textbox.insert("0.0", result_text)
        self.result_textbox.configure(state="disabled")

        self.restart_button = ctk.CTkButton(
            self.result_frame,
            text="New Analysis",
            command=self.restart,
            fg_color="#FF8C00",
            hover_color="#CC6A00",
            text_color="#000000"
        )
        self.restart_button.grid(row=1, column=0, pady=(0, 20))

        self.export_button = ctk.CTkButton(
            self.result_frame,
            text="Export CSV",
            command=lambda: self._export_results(result_text),
            fg_color="#555555",
            hover_color="#444444",
            text_color="#FFFFFF"
        )
        self.export_button.grid(row=1, column=1, pady=(0, 20), padx=(10, 0))

    def _export_results(self, text):
        fname = f"analysis_export.txt"
        try:
            with open(fname, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("Exported", f"Results exported to {fname}")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))

    def restart(self):
        if hasattr(self, 'result_frame'):
            self.result_frame.grid_forget()
        if hasattr(self, 'progress_frame'):
            self.progress_frame.grid_forget()
        if hasattr(self, 'input_frame'):
            self.input_frame.grid_forget()
        self.show_input()
