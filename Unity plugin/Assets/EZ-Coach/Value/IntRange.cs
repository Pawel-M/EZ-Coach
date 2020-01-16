using System;

namespace EZCoach.Value {
    [Serializable]
    public class IntRange {
        public readonly string type = "Range";
        public int min, max;

        public IntRange(int min, int max) {
            this.min = min;
            this.max = max;
        }

        public bool contains(int value) {
            return min <= value && value <= max;
        }
    }
}