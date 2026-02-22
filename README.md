# Motivation Behind Repo

An attempt to further my passion/intrigue for ops/systems thinking found during my gap year from Harvard. This repo is used to distill information from readings + program models I find interesting. Repo created in Spring 2026; updates to come with future projects undertaken during remaining gap + senior year.

## Directory Breakdown
1. Predictions Failures: Explaining ML's poor performance in continuous processing manufacturing
- The Goal: Predict machine output from ML. Working model (in theory) would ingest future runs supplied by operators, giving an expected output. Plant could "see into the future of their ops" based on their data.
- What I learned: How little I know about the dynamic, ever changing environment of manufacturing. Full commentary in predictions_failures/.


2. Simulation Tool: Discrete Event Simulator for discrete manufacturing
- The Goal: Build an interactive simulation tool demonstrating Factory Physics relationships (Little's Law, Kingman's approximation) to help understand how variability and utilization affect cycle time and WIP. Instead of trying to predict unpredictable outputs, simulate system behavior to explore what-if scenarios and test interventions before implementing them in production.
- What I learned: Simulation is more valuable than prediction in manufacturing. Learned the logic of queueing, variable arrival and processing times, and effects of high utilization in mfg environments.

### Books Read:
1. Factory Physics by Hopp & Spearman
    - The math models behind factory operations. Variability and high utilization directly blow up WIP/CT. Adding capacity is a bandaid over a deep wound; changes typically come from WIP caps and a focus on process.
2. The Goal by Goldratt
    - Theory of constraints. Added efficiency at non-bottleneck stations is a mirage, typically results in WIP blowup (hence cycle time inflation). Subordinating factory flow to the "beat" (throughput) of bottleneck resource results in optimal processing.
3. Designing ML Systems by Huyen
    - Both Data and Intelligent Design are important for ML efficacy. Batch processing (throughput) v stream processing (latency) depending on application. Data warehouse slow for data retrieval due to both read/write constraints, other data models (message broker Apache Kafka) are valuable. Got an overview on orchestrators/k8s. MLFlow is a useful service for experiment tracking.

Currently Reading:
- Matching Supply with Demand by Cachon
- Designing Data-Intensive Applications by Kleppmann

