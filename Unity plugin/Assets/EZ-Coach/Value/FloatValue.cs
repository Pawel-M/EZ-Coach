using System;

namespace EZCoach.Value {
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