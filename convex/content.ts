import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// Store creative content from Agent 3
export const store = mutation({
  args: {
    campaign_id: v.string(),
    days: v.array(v.any()),
    learning_data: v.any(),
    status: v.string(),
    timestamp: v.string(),
  },
  handler: async (ctx, args) => {
    // Check if content already exists for this campaign
    const existing = await ctx.db
      .query("content")
      .withIndex("by_campaign_id", (q) => q.eq("campaign_id", args.campaign_id))
      .first();

    if (existing) {
      // Update existing content
      await ctx.db.patch(existing._id, {
        days: args.days,
        learning_data: args.learning_data,
        status: args.status,
        timestamp: args.timestamp,
      });
      return { _id: existing._id, ...args };
    }

    // Create new content record
    const contentId = await ctx.db.insert("content", args);
    return { _id: contentId, ...args };
  },
});

// Get creative content for a campaign
export const get = query({
  args: {
    campaign_id: v.string(),
  },
  handler: async (ctx, args) => {
    const content = await ctx.db
      .query("content")
      .withIndex("by_campaign_id", (q) => q.eq("campaign_id", args.campaign_id))
      .first();

    if (!content) {
      return null;
    }

    return content;
  },
});
