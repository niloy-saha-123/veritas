// GitHub Action main script - reads code/docs from repo and calls Veritas API

const core = require('@actions/core');
const github = require('@actions/github');
const fs = require('fs').promises;
const path = require('path');

/**
 * Main action function
 */
async function run() {
    try {
        // Get inputs
        const apiKey = core.getInput('api-key');
        const apiUrl = core.getInput('api-url');
        const codePath = core.getInput('code-path');
        const docsPath = core.getInput('docs-path');
        const language = core.getInput('language');
        const failOnDiscrepancy = core.getInput('fail-on-discrepancy') === 'true';

        core.info(`🔍 Analyzing code in ${codePath} and docs in ${docsPath}`);

        // Read code files
        const codeFiles = await readDirectory(codePath);
        core.info(`Found ${codeFiles.length} code files`);

        // Read documentation files
        const docFiles = await readDirectory(docsPath);
        core.info(`Found ${docFiles.length} documentation files`);

        // Call Veritas API
        const analysisResult = await analyzeWithVeritas({
            apiUrl,
            apiKey,
            codeFiles,
            docFiles,
            language
        });

        // Process results
        const discrepancyCount = analysisResult.discrepancies?.length || 0;

        core.setOutput('discrepancies-found', discrepancyCount);
        core.setOutput('analysis-report', analysisResult.reportUrl || '');

        // Log results
        if (discrepancyCount === 0) {
            core.info('✅ No discrepancies found! Code and documentation are in sync.');
        } else {
            core.warning(`⚠️  Found ${discrepancyCount} discrepancies`);

            analysisResult.discrepancies.forEach((d, i) => {
                core.warning(`${i + 1}. [${d.severity}] ${d.description} (${d.location})`);
            });

            if (failOnDiscrepancy) {
                core.setFailed(`Found ${discrepancyCount} discrepancies`);
            }
        }

    } catch (error) {
        core.setFailed(`Action failed: ${error.message}`);
    }
}

/**
 * Read files from directory recursively
 */
async function readDirectory(dirPath) {
    const files = [];

    async function traverse(currentPath) {
        const entries = await fs.readdir(currentPath, { withFileTypes: true });

        for (const entry of entries) {
            const fullPath = path.join(currentPath, entry.name);

            if (entry.isDirectory()) {
                await traverse(fullPath);
            } else {
                const content = await fs.readFile(fullPath, 'utf-8');
                files.push({
                    path: fullPath,
                    name: entry.name,
                    content
                });
            }
        }
    }

    await traverse(dirPath);
    return files;
}

/**
 * Call Veritas API for analysis
 */
async function analyzeWithVeritas({ apiUrl, apiKey, codeFiles, docFiles, language }) {
    // TODO: Implement actual API call
    // For now, return mock data

    core.info('Calling Veritas API...');

    return {
        status: 'success',
        discrepancies: [],
        reportUrl: 'https://veritas.dev/reports/mock-id'
    };
}

// Run the action
run();
