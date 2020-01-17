using System;

namespace EZCoach.Value {
    /// <summary>
    /// The class representing the range of a floating-point value. It is limited by the minimum and maximum values.
    /// </summary>
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