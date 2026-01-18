from core.stats_manager import StatsManager

class StatsDisplay:
    @staticmethod
    def display_plot(stats: StatsManager):
        if not hasattr(stats, "weekly_total_time"):
            stats.compute_weekly_stats()
        print("\nLoading the plot. Please wait.....")
        import matplotlib.pyplot as plt
        title = "Weekly Report"
        plt.style.use('seaborn')
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(stats.weekly_dates, stats.weekly_minutes_spent, linewidth=3, marker='o', label='Minutes Spent')
        ax.plot(stats.weekly_dates, stats.weekly_pages_read, linewidth=3, marker='o', label='Pages Read')
        ax.legend()
        ax.set_title(f"{title} (Total Time: {stats.weekly_total_time})", fontsize=15)
        ax.set_xlabel("Date", fontsize=14)
        ax.set_ylabel("Minutes / Pages", fontsize=14)
        ax.tick_params(axis='both', labelsize=10)
        fig.autofmt_xdate()
        
        plt.tight_layout()
        plt.show(block=False)
        plt.pause(0.001)

    @staticmethod
    def show_weekly_stats(stats: StatsManager):
        print(stats.get_weekly_summary())
        
    
class CliProgressDisplay:

    @staticmethod
    def display_entries(heading: str, progress: dict) -> None:
        print(f"\n---------( {heading} )---------\n")
        for key, value in progress.items():
            print(f">>> {key}: {value}")

    @classmethod
    def display_entries_all(cls, progress: dict, day: str) -> None:
        print(f"\n<><><>--( Entries from {day} )--<><><>\n")
        if not progress:
            print(f">>> No entries recorded for {day}.")
            return
        for subject, books in progress.items():
            print(f"\n-----[<<( {subject} )>>]-----\n")
            for book, sessions in books.items():
                print(f"\n<><><>------[ {book} ]------<><><>\n")
                for session, session_details in sessions.items():
                    cls.display_entries(session, session_details)