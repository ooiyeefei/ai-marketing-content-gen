import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// Store analytics data from Agent 2
export const store = mutation({
  args: {
    campaign_id: v.string(),
    customer_sentiment: v.any(),
    past_performance: v.union(v.any(), v.null()),
    market_trends: v.any(),
    customer_photos: v.array(v.string()),
    timestamp: v.string(),
  },
  handler: async (ctx, args) => {
    // Check if analytics already exists for this campaign
    const existing = await ctx.db
      .query("analytics")
      .withIndex("by_campaign_id", (q) => q.eq("campaign_id", args.campaign_id))
      .first();

    if (existing) {
      // Update existing analytics
      await ctx.db.patch(existing._id, {
        customer_sentiment: args.customer_sentiment,
        past_performance: args.past_performance,
        market_trends: args.market_trends,
        customer_photos: args.customer_photos,
        timestamp: args.timestamp,
      });
      return { _id: existing._id, ...args };
    }

    // Create new analytics record
    const analyticsId = await ctx.db.insert("analytics", args);
    return { _id: analyticsId, ...args };
  },
});

// Get analytics data for a campaign
export const get = query({
  args: {
    campaign_id: v.string(),
  },
  handler: async (ctx, args) => {
    const analytics = await ctx.db
      .query("analytics")
      .withIndex("by_campaign_id", (q) => q.eq("campaign_id", args.campaign_id))
      .first();

    if (!analytics) {
      return null;
    }

    return analytics;
  },
});
