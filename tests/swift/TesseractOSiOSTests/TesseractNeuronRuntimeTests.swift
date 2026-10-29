import XCTest
@testable import TesseractOSiOS

private struct FixedEmbeddings: SemanticEmbeddingProvider {
    let scores: [String: Double]
    func similarity(between input: String, and description: String) async throws -> Double {
        scores.first(where: { description.contains($0.key) })?.value ?? 0
    }
}
private struct FixedExecutor: NeuronToolExecutor {
    let result: String
    func execute(toolID: String, input: String) async throws -> String { result }
}
final class TesseractNeuronRuntimeTests: XCTestCase {
    func testReadOnlyNeuronRunsAndAxonReturnsNextNeuron() async throws {
        let neuron = ToolNeuron(id: "search", name: "Search", description: "Find source material",
                                source: "test", suggestedNextNeuronIDs: ["summarize"])
        let next = ToolNeuron(id: "summarize", name: "Summarize", description: "Summarize sources", source: "test")
        let runtime = try TesseractNeuronRuntime(neurons: [neuron, next],
            embeddingProvider: FixedEmbeddings(scores: ["Search": 0.91, "Summarize": 0.2]),
            executor: FixedExecutor(result: "source found"))
        let result = try await runtime.process(NeuronSignal(text: "find source"))
        XCTAssertEqual(result.status, .completed)
        XCTAssertEqual(result.stage, .axon)
        XCTAssertEqual(result.selectedNeuronID, "search")
        XCTAssertEqual(result.output, "source found")
        XCTAssertEqual(result.suggestedNextNeuronIDs, ["summarize"])
        XCTAssertEqual(result.continuation, "OPEN")
    }
    func testExternalMutationIsBlockedByDefault() async throws {
        let neuron = ToolNeuron(id: "write", name: "Write", description: "Modify external state",
                                source: "test", effect: .externalMutation)
        let runtime = try TesseractNeuronRuntime(neurons: [neuron],
            embeddingProvider: FixedEmbeddings(scores: ["Write": 0.99]),
            executor: FixedExecutor(result: "must not run"))
        let result = try await runtime.process(NeuronSignal(text: "write"))
        XCTAssertEqual(result.status, .mutationBlocked)
        XCTAssertEqual(result.output, "EXTERNAL_MUTATION_BLOCKED_BY_POLICY")
    }
    func testNoSemanticMatchRemainsOpen() async throws {
        let neuron = ToolNeuron(id: "search", name: "Search", description: "Find source material", source: "test")
        let runtime = try TesseractNeuronRuntime(neurons: [neuron],
            embeddingProvider: FixedEmbeddings(scores: ["Search": 0.1]),
            executor: FixedExecutor(result: "unused"), minimumSimilarity: 0.72)
        let result = try await runtime.process(NeuronSignal(text: "unrelated"))
        XCTAssertEqual(result.status, .noMatch)
        XCTAssertEqual(result.stage, .dendrites)
        XCTAssertEqual(result.continuation, "OPEN")
    }
    func testDuplicateNeuronIDsAreRejected() {
        let a = ToolNeuron(id: "same", name: "A", description: "A", source: "test")
        let b = ToolNeuron(id: "same", name: "B", description: "B", source: "test")
        XCTAssertThrowsError(try TesseractNeuronRuntime(neurons: [a, b],
            embeddingProvider: FixedEmbeddings(scores: [:]), executor: FixedExecutor(result: "")))
    }
}
