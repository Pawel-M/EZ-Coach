using System;

namespace EZCoach.GridWorld {
    [Serializable]
    public struct PositionReward {
        public IntVector2 position;
        public float reward;
    }
}