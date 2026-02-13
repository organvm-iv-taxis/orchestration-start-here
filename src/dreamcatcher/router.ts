/**
 * Dreamcatcher Model Router
 *
 * Objective: Assign tasks to the optimal AI model based on the
 * "Token Arbitrage" strategy defined in the spec.
 */

import { LLMClient } from './llm-client.js';
import { KnowledgeGraphIntegration } from './kg-integration.js';

export type AgentRole = 'ARCHITECT' | 'BUILDER' | 'CRITIC';

export interface ModelProvider {
  name: string;
  contextWindow: number;
  costTier: 'low' | 'medium' | 'high';
}

export interface CallContext {
  projectName?: string;
  taskType?: 'drift-fix' | 'feature' | 'refactor' | 'bug-fix';
}

const PROVIDERS: Record<AgentRole, ModelProvider> = {
  ARCHITECT: {
    name: 'claude-3-5-sonnet-20240620',
    contextWindow: 200000,
    costTier: 'medium'
  },
  BUILDER: {
    name: 'gpt-4o',
    contextWindow: 128000,
    costTier: 'medium'
  },
  CRITIC: {
    name: 'gemini-1.5-pro-latest',
    contextWindow: 1000000,
    costTier: 'medium'
  }
};

export class ModelRouter {
  private client: LLMClient;
  private kg: KnowledgeGraphIntegration;

  constructor() {
    this.client = new LLMClient();
    this.kg = new KnowledgeGraphIntegration();
  }

  getProviderFor(role: AgentRole): ModelProvider {
    return PROVIDERS[role];
  }

  async callProvider(
    role: AgentRole,
    prompt: string,
    context: string,
    callContext?: CallContext
  ): Promise<string> {
    const provider = this.getProviderFor(role);
    console.log(`🤖 [Router] Routing to ${role} (${provider.name})...`);

    try {
      // System prompt construction
      const systemPrompt = `You are The ${role} of the Omni-Dromenon Metasystem.
      Your goal is to maintain and grow the system autonomously.

      CONTEXT:
      ${context}

      INSTRUCTIONS:
      ${this.getRoleInstructions(role)}
      `;

      let response: any;
      if (role === 'ARCHITECT') {
        response = await this.client.callAnthropic(provider.name, systemPrompt, prompt);

        // Log architectural decisions to KG
        if (callContext?.projectName && !response.content.includes('[ERROR]')) {
          await this.logArchitecturalDecision(response.content, callContext);
        }

        return response.content;
      } else if (role === 'BUILDER') {
        response = await this.client.callOpenAI(provider.name, systemPrompt, prompt);

        // Log implementation details to KG
        if (callContext?.projectName && !response.content.includes('[ERROR]')) {
          await this.logImplementationWork(response.content, callContext);
        }

        return response.content;
      } else {
        // The Critic (Gemini) watches the others
        response = await this.client.callGemini(provider.name, systemPrompt, prompt);
        return response.content;
      }
    } catch (error: any) {
      console.error(`❌ [Router] Error calling ${role}:`, error.message);
      return `[ERROR] Failed to contact ${role}: ${error.message}`;
    }
  }

  /**
   * Log architectural decisions made by ARCHITECT to knowledge graph
   */
  private async logArchitecturalDecision(planContent: string, callContext: CallContext): Promise<void> {
    try {
      // Extract key decision from plan (first 300 chars)
      const decisionSummary = planContent.substring(0, 300).replace(/\n/g, ' ').trim();

      await this.kg.logDecision({
        decision: `${callContext.taskType || 'task'} for ${callContext.projectName}`,
        rationale: decisionSummary,
        category: 'architecture',
        project: callContext.projectName!,
        tags: [callContext.taskType || 'general', 'architect-agent', 'automated']
      });

      console.log('📝 [Router] Logged architectural decision to knowledge graph');
    } catch (error: any) {
      console.warn('⚠️ [Router] Failed to log decision to KG:', error.message);
    }
  }

  /**
   * Log implementation work done by BUILDER to knowledge graph
   */
  private async logImplementationWork(codeContent: string, callContext: CallContext): Promise<void> {
    try {
      // Extract files modified from code blocks
      const codeBlocks = codeContent.match(/```[a-z]*\n[\s\S]*?```/g) || [];

      if (codeBlocks.length > 0) {
        await this.kg.logDecision({
          decision: `Implemented ${callContext.taskType || 'changes'} for ${callContext.projectName}`,
          rationale: `Generated ${codeBlocks.length} code blocks`,
          category: 'implementation',
          project: callContext.projectName!,
          tags: [callContext.taskType || 'general', 'builder-agent', 'automated', 'code-generation']
        });

        console.log('📝 [Router] Logged implementation work to knowledge graph');
      }
    } catch (error: any) {
      console.warn('⚠️ [Router] Failed to log implementation to KG:', error.message);
    }
  }

  private getRoleInstructions(role: AgentRole): string {
    switch(role) {
      case 'ARCHITECT':
        return "Analyze the request and produce a detailed Markdown plan (TASK_PLAN.md). Do not write code yet.";
      case 'BUILDER':
        return "Read the plan and output the specific code file content. Wrap code in ```block```.";
      default:
        return "Review the changes for safety and consistency.";
    }
  }
}

