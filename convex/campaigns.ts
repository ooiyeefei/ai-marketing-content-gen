import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// Create new campaign
export const create = mutation({
  args: {
    campaign_id: v.string(),
    status: v.string(),
    progress: v.number(),
    current_agent: v.union(v.string(), v.null()),
    message: v.string(),
  },
  handler: async (ctx, args) => {
    const now = Date.now();

    const campaignId = await ctx.db.insert("campaigns", {
      campaign_id: args.campaign_id,
      status: args.status,
      progress: args.progress,
      current_agent: args.current_agent,
      message: args.message,
      created_at: now,
      updated_at: now,
    });

    return { _id: campaignId, ...args, created_at: now, updated_at: now };
  },
});

// Update campaign progress
export const updateProgress = mutation({
  args: {
    campaign_id: v.string(),
    status: v.string(),
    progress: v.number(),
    current_agent: v.union(v.string(), v.null()),
    message: v.string(),
  },
  handler: async (ctx, args) => {
    const campaign = await ctx.db
      .query("campaigns")
      .withIndex("by_campaign_id", (q) => q.eq("campaign_id", args.campaign_id))
      .first();

    if (!campaign) {
      throw new Error(`Campaign not found: ${args.campaign_id}`);
    }

    const now = Date.now();
    await ctx.db.patch(campaign._id, {
      status: args.status,
      progress: args.progress,
      current_agent: args.current_agent,
      message: args.message,
      updated_at: now,
    });

    return { _id: campaign._id, ...args, updated_at: now };
  },
});

// Get campaign progress
export const getProgress = query({
  args: {
    campaign_id: v.string(),
  },
  handler: async (ctx, args) => {
    const campaign = await ctx.db
      .query("campaigns")
      .withIndex("by_campaign_id", (q) => q.eq("campaign_id", args.campaign_id))
      .first();

    if (!campaign) {
      return null;
    }

    return {
      campaign_id: campaign.campaign_id,
      status: campaign.status,
      percentage: campaign.progress,
      current_agent: campaign.current_agent,
      message: campaign.message,
      created_at: campaign.created_at,
      updated_at: campaign.updated_at,
    };
  },
});
