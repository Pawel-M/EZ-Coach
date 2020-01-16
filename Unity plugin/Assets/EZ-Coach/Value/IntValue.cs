using System;

namespace EZCoach.Value {
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