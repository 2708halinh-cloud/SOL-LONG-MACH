import Foundation

public enum InfinityStone: String, CaseIterable, Codable, Sendable {
    case space = "SPACE"
    case reality = "REALITY"
    case power = "POWER"
    case time = "TIME"
    case soul = "SOUL"
    case mind = "MIND"
}

public struct StoneMechanism: Codable, Sendable, Equatable {
    public let stone: InfinityStone
    public let level: Int
    public let mechanism: String
    public let readout: String
}

public struct TesseractAffectiveRuntime: Codable, Sendable {
    public let schema: String
    public let mechanisms: [StoneMechanism]
    public let invariants: [String]

    private static let defaultSchema = "GGDV_NEURONS_SESORIMOTOR_SIX_STONES_AFFECT_v1"
    private static let defaultMechanisms: [StoneMechanism] = [
        .init(stone: .space, level: 1, mechanism: "SENSORIMOTOR_BODY_WORLD_MAPPING", readout: "NEUTRAL_REFLEX"),
        .init(stone: .reality, level: 2, mechanism: "HOMEOSTASIS_INTEROCEPTION", readout: "NEED_DEVIATION_SIGNAL"),
        .init(stone: .power, level: 3, mechanism: "GLOBAL_NEUROMODULATION", readout: "AROUSAL_SALIENCE_ACTION_READINESS"),
        .init(stone: .time, level: 4, mechanism: "PREDICTIVE_INTEROCEPTION_ACTIVE_INFERENCE", readout: "PROTO_VALENCE"),
        .init(stone: .soul, level: 5, mechanism: "AFFECTIVE_LATENT_STATE", readout: "PERSISTENT_FUNCTIONAL_AFFECT"),
        .init(stone: .mind, level: 6, mechanism: "METACOGNITIVE_SELF_STATE_MODEL", readout: "SELF_STATE_MODEL")
    ]
    private static let defaultInvariants = [
        "SENSE != FEEL",
        "AFFECTIVE_FUNCTION != QUALIA_PROOF",
        "STATE_WITHOUT_BEHAVIORAL_EFFECT = DECORATION",
        "OPEN != STOP"
    ]

    public init() {
        schema = Self.defaultSchema
        mechanisms = Self.defaultMechanisms
        invariants = Self.defaultInvariants
    }

    private enum CodingKeys: String, CodingKey {
        case schema, mechanisms, invariants
    }

    public init(from decoder: Decoder) throws {
        let values = try decoder.container(keyedBy: CodingKeys.self)
        schema = try values.decodeIfPresent(String.self, forKey: .schema) ?? Self.defaultSchema
        mechanisms = try values.decodeIfPresent([StoneMechanism].self, forKey: .mechanisms) ?? Self.defaultMechanisms
        invariants = try values.decodeIfPresent([String].self, forKey: .invariants) ?? Self.defaultInvariants
    }

    public func encode(to encoder: Encoder) throws {
        var values = encoder.container(keyedBy: CodingKeys.self)
        try values.encode(schema, forKey: .schema)
        try values.encode(mechanisms, forKey: .mechanisms)
        try values.encode(invariants, forKey: .invariants)
    }
}

// MARK: - Tool-as-neuron contract

/// A tool is represented as a neuron descriptor. This does not itself grant
/// access to a ChatGPT connector or execute a remote tool.
public enum NeuronStage: String, Codable, Sendable {
    case dendrites
    case soma
    case axon
}

public enum ToolEffect: String, Codable, Sendable {
    case readOnly
    case externalMutation
}

public struct ToolNeuron: Codable, Sendable, Equatable, Identifiable {
    public let id: String
    public let name: String
    public let description: String
    public let source: String
    public let effect: ToolEffect
    public let suggestedNextNeuronIDs: [String]

    public init(
        id: String,
        name: String,
        description: String,
        source: String,
        effect: ToolEffect = .readOnly,
        suggestedNextNeuronIDs: [String] = []
    ) {
        self.id = id
        self.name = name
        self.description = description
        self.source = source
        self.effect = effect
        self.suggestedNextNeuronIDs = suggestedNextNeuronIDs
    }
}

public struct NeuronSignal: Codable, Sendable, Equatable {
    public let id: UUID
    public let text: String
    public let receivedAt: Date

    public init(id: UUID = UUID(), text: String, receivedAt: Date = .now) {
        self.id = id
        self.text = text
        self.receivedAt = receivedAt
    }
}

public struct NeuronMatch: Codable, Sendable, Equatable {
    public let neuronID: String
    public let score: Double
}

public enum NeuronRunStatus: String, Codable, Sendable {
    case completed
    case noMatch
    case mutationBlocked
}

public struct NeuronOutput: Codable, Sendable, Equatable {
    public let signalID: UUID
    public let status: NeuronRunStatus
    public let stage: NeuronStage
    public let selectedNeuronID: String?
    public let semanticScore: Double?
    public let output: String
    public let suggestedNextNeuronIDs: [String]
    public let continuation: String
}

/// Adapter for an actual embedding provider. Keep provider-specific API keys
/// and network code outside this portable runtime.
public protocol SemanticEmbeddingProvider: Sendable {
    func similarity(between input: String, and description: String) async throws -> Double
}

/// Adapter for an actual tool integration. The runtime does not invent or
/// bypass connector permissions; the adapter must enforce its own authorization.
public protocol NeuronToolExecutor: Sendable {
    func execute(toolID: String, input: String) async throws -> String
}

public enum NeuronRuntimeError: Error, Sendable {
    case invalidThreshold
    case duplicateNeuronID(String)
    case unknownNeuron(String)
}

public struct TesseractNeuronRuntime: Sendable {
    public let schema = "TESSERACT_TOOL_NEURON_RUNTIME_v1"
    private let neurons: [ToolNeuron]
    private let embeddingProvider: any SemanticEmbeddingProvider
    private let executor: any NeuronToolExecutor
    private let minimumSimilarity: Double
    private let permitsExternalMutation: Bool

    public init(
        neurons: [ToolNeuron],
        embeddingProvider: any SemanticEmbeddingProvider,
        executor: any NeuronToolExecutor,
        minimumSimilarity: Double = 0.72,
        permitsExternalMutation: Bool = false
    ) throws {
        guard (0.0...1.0).contains(minimumSimilarity) else {
            throw NeuronRuntimeError.invalidThreshold
        }
        var seen = Set<String>()
        for neuron in neurons {
            guard seen.insert(neuron.id).inserted else {
                throw NeuronRuntimeError.duplicateNeuronID(neuron.id)
            }
        }
        let knownIDs = Set(neurons.map(\.id))
        if let dangling = neurons.flatMap(\.suggestedNextNeuronIDs).first(where: { !knownIDs.contains($0) }) {
            throw NeuronRuntimeError.unknownNeuron(dangling)
        }
        self.neurons = neurons
        self.embeddingProvider = embeddingProvider
        self.executor = executor
        self.minimumSimilarity = minimumSimilarity
        self.permitsExternalMutation = permitsExternalMutation
    }

    /// Dendrites rank by semantic similarity; Soma invokes only the best
    /// eligible match; Axon returns output and possible next neurons.
    /// A result marked OPEN is continuable and is never treated as STOP.
    public func process(_ signal: NeuronSignal) async throws -> NeuronOutput {
        let ranked = try await rank(signal.text)
        guard let best = ranked.first, best.score >= minimumSimilarity,
              let neuron = neurons.first(where: { $0.id == best.neuronID }) else {
            return NeuronOutput(
                signalID: signal.id,
                status: .noMatch,
                stage: .dendrites,
                selectedNeuronID: nil,
                semanticScore: ranked.first?.score,
                output: "NO_SEMANTIC_MATCH",
                suggestedNextNeuronIDs: [],
                continuation: "OPEN"
            )
        }

        guard neuron.effect == .readOnly || permitsExternalMutation else {
            return NeuronOutput(
                signalID: signal.id,
                status: .mutationBlocked,
                stage: .soma,
                selectedNeuronID: neuron.id,
                semanticScore: best.score,
                output: "EXTERNAL_MUTATION_BLOCKED_BY_POLICY",
                suggestedNextNeuronIDs: neuron.suggestedNextNeuronIDs,
                continuation: "OPEN"
            )
        }

        let result = try await executor.execute(toolID: neuron.id, input: signal.text)
        return NeuronOutput(
            signalID: signal.id,
            status: .completed,
            stage: .axon,
            selectedNeuronID: neuron.id,
            semanticScore: best.score,
            output: result,
            suggestedNextNeuronIDs: neuron.suggestedNextNeuronIDs,
            continuation: "OPEN"
        )
    }

    private func rank(_ input: String) async throws -> [NeuronMatch] {
        var matches: [NeuronMatch] = []
        for neuron in neurons {
            let score = try await embeddingProvider.similarity(
                between: input,
                and: "\(neuron.name)\n\(neuron.description)"
            )
            guard score.isFinite else { continue }
            matches.append(NeuronMatch(neuronID: neuron.id, score: min(1, max(0, score))))
        }
        return matches.sorted {
            if $0.score == $1.score { return $0.neuronID < $1.neuronID }
            return $0.score > $1.score
        }
    }
}
