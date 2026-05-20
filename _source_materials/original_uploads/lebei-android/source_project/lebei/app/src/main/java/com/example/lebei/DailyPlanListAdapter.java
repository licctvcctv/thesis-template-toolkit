package com.example.lebei;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import java.util.ArrayList;
import java.util.List;

public class DailyPlanListAdapter extends RecyclerView.Adapter<DailyPlanListAdapter.VH> {

    public interface OnPlanClickListener {
        void onPlanClick(long planId);
    }

    public static final class Row {
        public final DailyPlan plan;
        public final int wordCount;

        public Row(DailyPlan plan, int wordCount) {
            this.plan = plan;
            this.wordCount = wordCount;
        }
    }

    private final List<Row> data = new ArrayList<>();
    private OnPlanClickListener listener;

    public void setOnPlanClickListener(OnPlanClickListener listener) {
        this.listener = listener;
    }

    public void setData(List<Row> rows) {
        data.clear();
        if (rows != null) {
            data.addAll(rows);
        }
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public VH onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View v =
                LayoutInflater.from(parent.getContext())
                        .inflate(R.layout.item_daily_plan, parent, false);
        return new VH(v);
    }

    @Override
    public void onBindViewHolder(@NonNull VH holder, int position) {
        Row row = data.get(position);
        DailyPlan p = row.plan;
        holder.title.setText(p.dateKey + " · " + BookLabels.nameForBookId(p.bookId));
        String sub = row.wordCount + " 个单词";
        if (p.essayText != null && !p.essayText.trim().isEmpty()) {
            sub += " · 已保存短文";
        }
        holder.sub.setText(sub);
        holder.itemView.setOnClickListener(
                v -> {
                    if (listener != null) {
                        listener.onPlanClick(p.id);
                    }
                });
    }

    @Override
    public int getItemCount() {
        return data.size();
    }

    static final class VH extends RecyclerView.ViewHolder {
        final TextView title;
        final TextView sub;

        VH(@NonNull View itemView) {
            super(itemView);
            title = itemView.findViewById(R.id.tv_plan_title);
            sub = itemView.findViewById(R.id.tv_plan_sub);
        }
    }
}
