using System;

namespace EZCoach.Value {
    /// <summary>
    /// The class representing a definition of a single integer value.
    /// </summary>
    [Serializable]
    public class IntValue {
        public readonly string type = "IntValue";
        public IntRange range;
        public string description;
        public IntValue(IntRange range, string description) {
            this.range = range;
            this.description = description;
        }
    }
}