package com.example.lebei;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import com.example.lebei.api.LeaderboardEntry;
import java.util.ArrayList;
import java.util.List;

public class LeaderboardAdapter extends RecyclerView.Adapter<RecyclerView.ViewHolder> {

    private static final int TYPE_HEADER = 0;
    private static final int TYPE_ROW = 1;

    private final List<LeaderboardEntry> rows = new ArrayList<>();

    void setRows(List<LeaderboardEntry> list) {
        rows.clear();
        if (list != null) {
            rows.addAll(list);
        }
        notifyDataSetChanged();
    }

    @Override
    public int getItemViewType(int position) {
        return position == 0 ? TYPE_HEADER : TYPE_ROW;
    }

    @Override
    public int getItemCount() {
        return rows.isEmpty() ? 0 : 1 + rows.size();
    }

    @NonNull
    @Override
    public RecyclerView.ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        LayoutInflater inflater = LayoutInflater.from(parent.getContext());
        if (viewType == TYPE_HEADER) {
            View v = inflater.inflate(R.layout.item_leaderboard_header, parent, false);
            return new HeaderHolder(v);
        }
        View v = inflater.inflate(R.layout.item_leaderboard_row, parent, false);
        return new RowHolder(v);
    }

    @Override
    public void onBindViewHolder(@NonNull RecyclerView.ViewHolder holder, int position) {
        if (holder instanceof RowHolder) {
            LeaderboardEntry e = rows.get(position - 1);
            RowHolder h = (RowHolder) holder;
            h.tvRank.setText(String.valueOf(e.getRank()));
            h.tvUsername.setText(e.getUsername());
            h.tvLearned.setText(String.valueOf(e.getLearnedWordsCount()));
            h.tvMastered.setText(String.valueOf(e.getMasteredWordsCount()));
            h.tvPoints.setText(String.valueOf(e.getStudyPoints()));
            h.tvToday.setText(String.valueOf(e.getTodayLearnedCount()));
        }
    }

    static final class HeaderHolder extends RecyclerView.ViewHolder {
        HeaderHolder(@NonNull View itemView) {
            super(itemView);
        }
    }

    static final class RowHolder extends RecyclerView.ViewHolder {
        final TextView tvRank, tvUsername, tvLearned, tvMastered, tvPoints, tvToday;

        RowHolder(@NonNull View itemView) {
            super(itemView);
            tvRank = itemView.findViewById(R.id.tv_rank);
            tvUsername = itemView.findViewById(R.id.tv_username);
            tvLearned = itemView.findViewById(R.id.tv_learned_words);
            tvMastered = itemView.findViewById(R.id.tv_mastered_words);
            tvPoints = itemView.findViewById(R.id.tv_points);
            tvToday = itemView.findViewById(R.id.tv_today);
        }
    }
}
