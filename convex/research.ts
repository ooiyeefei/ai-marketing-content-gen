import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// Store research data from Agent 1
export const store = mutation({
  args: {
    campaign_id: v.string(),
    business_context: v.any(),
    competitors: v.array(v.any()),
    market_insights: v.any(),
    research_images: v.array(v.string()),
    timestamp: v.string(),
  },
  handler: async (ctx, args) => {
    // Check if research already exists for this campaign
    const existing = await ctx.db
      .query("research")
      .withIndex("by_campaign_id", (q) => q.eq("campaign_id", args.campaign_id))
      .first();

    if (existing) {
      // Update existing research
      await ctx.db.patch(existing._id, {
        business_context: args.business_context,
        competitors: args.competitors,
        market_insights: args.market_insights,
        research_images: args.research_images,
        timestamp: args.timestamp,
      });
      return { _id: existing._id, ...args };
    }

    // Create new research record
    const researchId = await ctx.db.insert("research", args);
    return { _id: researchId, ...args };
  },
});

// Get research data for a campaign
export const get = query({
  args: {
    campaign_id: v.string(),
  },
  handler: async (ctx, args) => {
    const research = await ctx.db
      .query("research")
      .withIndex("by_campaign_id", (q) => q.eq("campaign_id", args.campaign_id))
      .first();

    if (!research) {
      return null;
    }

    return research;
  },
});
