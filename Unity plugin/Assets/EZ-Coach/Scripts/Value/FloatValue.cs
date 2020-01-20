using System;

namespace EZCoach.Value {
    /// <summary>
    /// The class representing a definition of a single floating-point value.
    /// </summary>
    [Serializable]
    public class FloatValue {
        
        public readonly string type = "FloatValue";
        public FloatRange range;
        public string description;
        public FloatValue(FloatRange range, string description) {
            this.range = range;
            this.description = description;
        }
    }
}