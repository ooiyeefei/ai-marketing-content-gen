import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  // Campaign progress tracking
  campaigns: defineTable({
    campaign_id: v.string(),
    status: v.string(),
    progress: v.number(),
    current_agent: v.union(v.string(), v.null()),
    message: v.string(),
    created_at: v.number(),
    updated_at: v.number(),
  }).index("by_campaign_id", ["campaign_id"]),

  // Agent 1: Research data
  research: defineTable({
    campaign_id: v.string(),
    business_context: v.any(), // Complex nested object
    competitors: v.array(v.any()),
    market_insights: v.any(),
    research_images: v.array(v.string()),
    timestamp: v.string(),
  }).index("by_campaign_id", ["campaign_id"]),

  // Agent 2: Analytics data
  analytics: defineTable({
    campaign_id: v.string(),
    customer_sentiment: v.any(),
    past_performance: v.union(v.any(), v.null()),
    market_trends: v.any(),
    customer_photos: v.array(v.string()),
    timestamp: v.string(),
  }).index("by_campaign_id", ["campaign_id"]),

  // Agent 3: Creative content
  content: defineTable({
    campaign_id: v.string(),
    days: v.array(v.any()),
    learning_data: v.any(),
    status: v.string(),
    timestamp: v.string(),
  }).index("by_campaign_id", ["campaign_id"]),
});
