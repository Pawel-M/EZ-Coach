using System;
using System.Collections.Generic;

namespace EZCoach.Value {
    /// <summary>
    /// The class representing a definition of a value in the form of list of floats.
    /// </summary>
    [Serializable]
    public class FloatList {
        public readonly string type = "FloatList";
        public IEnumerable<FloatRange> ranges;
        public string description;

        public FloatList(IEnumerable<FloatRange> ranges, string description = null) {
            this.ranges = ranges;
            this.description = description;
        }

        public FloatList(int size, FloatRange range, string description = null) {
            this.description = description;

            var arrayRanges = new FloatRange[size];
            for (int i = 0; i < size; i++) {
                arrayRanges[i] = range;
            }

            ranges = arrayRanges;
        }
    }
}