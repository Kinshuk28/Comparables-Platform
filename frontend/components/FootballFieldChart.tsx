"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { FootballField } from "@/lib/types";
import { formatMoney } from "@/lib/format";

export default function FootballFieldChart({ footballField }: { footballField: FootballField }) {
  const { bars, offer_price, current_share_price } = footballField;

  if (bars.length === 0) {
    return <p className="text-sm text-slate-500">No valuation ranges available to chart.</p>;
  }

  const data = bars.map((b) => ({
    method: b.method,
    low: b.low,
    range: Math.max(b.high - b.low, 0),
    high: b.high,
    mid: b.mid,
  }));

  const allValues = bars.flatMap((b) => [b.low, b.high, b.mid, offer_price, current_share_price ?? b.low]);
  const maxValue = Math.max(...allValues);
  const minValue = Math.min(0, ...allValues);
  const domain: [number, number] = [minValue, Math.ceil(maxValue * 1.15)];

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e5eb" />
          <XAxis type="number" domain={domain} tickFormatter={(v) => `$${v}`} stroke="#64748b" fontSize={12} />
          <YAxis type="category" dataKey="method" width={190} stroke="#64748b" fontSize={12} />
          <Tooltip
            formatter={(value: number, name: string, props: { payload?: { low: number; high: number } }) => {
              if (name === "range" && props.payload) {
                return [`${formatMoney(props.payload.low)} – ${formatMoney(props.payload.high)}`, "Implied range"];
              }
              return [formatMoney(value), name];
            }}
          />
          <Bar dataKey="low" stackId="range" fill="transparent" isAnimationActive={false} />
          <Bar dataKey="range" stackId="range" fill="#1e2f4d" radius={[3, 3, 3, 3]} barSize={28} isAnimationActive={false} />
          <ReferenceLine
            x={offer_price}
            stroke="#b8934a"
            strokeWidth={2}
            label={{ value: `Offer ${formatMoney(offer_price)}`, position: "top", fill: "#b8934a", fontSize: 12 }}
          />
          {current_share_price ? (
            <ReferenceLine
              x={current_share_price}
              stroke="#64748b"
              strokeDasharray="4 4"
              label={{ value: `Current ${formatMoney(current_share_price)}`, position: "insideTopLeft", fill: "#64748b", fontSize: 11 }}
            />
          ) : null}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
