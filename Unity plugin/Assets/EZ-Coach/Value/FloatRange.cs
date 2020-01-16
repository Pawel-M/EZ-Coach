using System;

namespace EZCoach.Value {
    [Serializable]
    public class FloatRange {
        public readonly string type = "Range";
        public float min, max;

        public FloatRange(float min, float max) {
            this.min = min;
            this.max = max;
        }

        public bool contains(int value) {
            return min <= value && value <= max;
        }
    }
}