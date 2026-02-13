/**
 * Dreamcatcher Night Watchman
 * 
 * Objective: The autonomous event loop that monitors the system for
 * idle bandwidth and dispatches agents to perform work.
 */

import { CircuitBreaker } from './circuit.js';
import { ModelRouter } from './router.js';
import { MetasystemManager } from '../orchestrator/metasystem-manager.js';
import { SCENARIOS, Scenario } from './scenarios/index.js';
import { KnowledgeGraphIntegration } from './kg-integration.js';

export class NightWatchman {
  private circuit: CircuitBreaker;
  private router: ModelRouter;
  private metasystem: MetasystemManager;
  private kg: KnowledgeGraphIntegration;
  private isAwake: boolean = false;

  constructor(metasystem: MetasystemManager) {
    this.metasystem = metasystem;
    this.circuit = new CircuitBreaker();
    this.router = new ModelRouter();
    this.kg = new KnowledgeGraphIntegration();
  }

  startWatch(): void {
    if (this.isAwake) return;
    this.isAwake = true;
    console.log('🌙 [Watchman] The Night Watch begins. Scanning for dreams...');
    
    // Start the poll loop (every 1 minute for demo, 1 hour in prod)
    setInterval(() => this.patrol(), 60000);
  }

  private async patrol() {
    if (!this.circuit.canProceed()) return;

    // 1. Process Pending Tasks (The "Doing")
    await this.processInbox();

    // 2. Check Universe Health (The "Seeing")
    const health = await this.metasystem.getUniverseHealth();
    
    // 3. Identify Drift
    const drifted = health.filter(h => h.status === 'drifted' || h.status === 'error');

    if (drifted.length > 0) {
      console.log(`🌙 [Watchman] Found ${drifted.length} drifted dreams.`);
      
      for (const project of drifted) {
        if (!this.circuit.canProceed()) break;

        await this.handleDrift(project);
        this.circuit.registerLoop();
      }
    } else {
      console.log('🌙 [Watchman] The universe is calm.');
      
      // 4. Entropy / Dream Scenarios (The "Dreaming")
      // 5% chance to trigger a scenario if calm
      if (Math.random() < 0.05) {
        const randomScenario = SCENARIOS[Math.floor(Math.random() * SCENARIOS.length)];
        await this.runScenario(randomScenario);
      }
    }
  }

  public async runScenario(scenario: Scenario) {
    console.log(`✨ [Watchman] Initiating Dream Scenario: ${scenario.name}`);

    // Query KG for relevant context before planning
    console.log('🔍 [Watchman] Querying knowledge graph for context...');
    const [pastDecisions, similarWork] = await Promise.all([
      this.kg.findPastDecisions(scenario.name, 'omni-dromenon-machina'),
      this.kg.findSimilarWork(scenario.description, 'omni-dromenon-machina')
    ]);

    // Build enriched context
    let kgContext = '\n## KNOWLEDGE GRAPH CONTEXT\n\n';

    if (pastDecisions.length > 0) {
      kgContext += '### Past Decisions:\n';
      pastDecisions.slice(0, 5).forEach(d => {
        kgContext += `- **${d.decision}**: ${d.rationale} (${d.category})\n`;
      });
      kgContext += '\n';
    }

    if (similarWork.length > 0) {
      kgContext += '### Similar Work in Other Projects:\n';
      similarWork.forEach(w => {
        kgContext += `- **${w.project}**: ${w.decision} - ${w.rationale}\n`;
      });
      kgContext += '\n';
    }

    const plan = await this.router.callProvider(
      'ARCHITECT',
      scenario.prompt,
      `Context: 4jp-metasystem.yaml\n${kgContext}`,
      {
        projectName: 'omni-dromenon-machina',
        taskType: 'feature'
      }
    );

    await this.metasystem.dispatcher.dispatchTask({
        workspaceName: 'omni-dromenon-machina', // Scenarios often span the metasystem
        taskType: 'feature',
        title: `Dream: ${scenario.name}`,
        description: `## SCENARIO: ${scenario.name}\n${scenario.description}\n\n## KNOWLEDGE GRAPH INSIGHTS\n${kgContext}\n\n## PLAN\n${plan}`,
        priority: 'low'
    });

    this.circuit.registerLoop();
  }


  private async processInbox() {
      // Placeholder: In a real system, this reads from .orchestrator/inbox
      // For now, we assume the Dispatcher handles the handoff or we implement a simple queue
      console.log('🌙 [Watchman] Checking inbox...');
  }

  private async handleDrift(project: any) {
    console.log(`🌙 [Watchman] Dispatching Architect to fix ${project.name}...`);

    // Step 0: Query Knowledge Graph for Context
    console.log('🔍 [Watchman] Querying knowledge graph for project context...');
    const [projectContext, pastDecisions, recentFiles, similarWork] = await Promise.all([
      this.kg.getProjectContext(project.name, 168), // Last week
      this.kg.findPastDecisions('drift architecture', project.name),
      this.kg.findRecentFileChanges(project.name, 48), // Last 2 days
      this.kg.findSimilarWork(`fix drift in ${project.missing_modules?.join(' ')}`, project.name)
    ]);

    // Build Knowledge Graph Context
    let kgContext = '\n## KNOWLEDGE GRAPH CONTEXT\n\n';

    kgContext += `### Project: ${project.name}\n`;
    kgContext += `- Recent Decisions: ${projectContext.recent_decisions.length}\n`;
    kgContext += `- Recent File Changes: ${projectContext.recent_files.length}\n\n`;

    if (pastDecisions.length > 0) {
      kgContext += '### Past Decisions Related to Drift:\n';
      pastDecisions.slice(0, 3).forEach(d => {
        kgContext += `- **${d.decision}**: ${d.rationale}\n`;
      });
      kgContext += '\n';
    }

    if (recentFiles.length > 0) {
      kgContext += '### Recently Modified Files:\n';
      recentFiles.slice(0, 5).forEach(f => {
        kgContext += `- ${f.path} (${f.operation}, ${f.modified_at})\n`;
      });
      kgContext += '\n';
    }

    if (similarWork.length > 0) {
      kgContext += '### Similar Work in Other Projects:\n';
      similarWork.slice(0, 3).forEach(w => {
        kgContext += `- **${w.project}**: ${w.decision} - ${w.rationale}\n`;
      });
      kgContext += '\n';
    }

    // Phase 1: Planning (Claude) with KG Context
    const plan = await this.router.callProvider(
      'ARCHITECT',
      `Analyze drift in ${project.name}. Missing modules: ${project.missing_modules?.join(', ')}\n\n${kgContext}`,
      `Context: 4jp-metasystem.yaml. Project Genome: ${project.name}`,
      {
        projectName: project.name,
        taskType: 'drift-fix'
      }
    );

    // Phase 2: Critical Review (Gemini) - "Who watches the watchmen?"
    console.log(`🌙 [Watchman] Dispatching Critic to review Architect's plan for ${project.name}...`);
    const review = await this.router.callProvider(
      'CRITIC',
      `Critically review the following plan for ${project.name}.

      MANDATORY CHECKS:
      1. Does it violate any 'non_goals' defined in 'seed.yaml'?
      2. Does it respect the 'automation_contract' (e.g. disallowed_writes)?
      3. Is it aligned with the 'problem_statement'?
      4. Does it consider past decisions and similar work from knowledge graph?

      KNOWLEDGE GRAPH CONTEXT:
      ${kgContext}

      PLAN:
      ${plan}`,
      'Context: Project Genome (seed.yaml) & Security Mandates.'
    );

    console.log(`🌙 [Watchman] Critic's Verdict: ${review.substring(0, 100)}...`);

    // Phase 3: Manifestation
    await this.metasystem.dispatcher.dispatchTask({
        workspaceName: project.name,
        taskType: 'ai-fix',
        title: `Auto-Fix Drift: ${project.name} (Reviewed by Critic)`,
        description: `## KNOWLEDGE GRAPH INSIGHTS\n${kgContext}\n\n## ARCHITECT PLAN\n${plan}\n\n## CRITIC REVIEW\n${review}`,
        priority: 'high'
    });

    // Log the decision to fix drift
    await this.kg.logDecision({
      decision: `Fix drift in ${project.name}: ${project.missing_modules?.join(', ')}`,
      rationale: plan.substring(0, 500), // First 500 chars of plan
      category: 'architecture',
      project: project.name,
      tags: ['drift', 'auto-fix', ...project.missing_modules || []]
    });
  }
}
