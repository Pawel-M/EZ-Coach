using System;
using System.Collections.Generic;

namespace EZCoach.Value {
    [Serializable]
    public class IntList {
        public readonly string type = "IntList";
        public IEnumerable<IntRange> ranges;
        public string description;

        public IntList(IEnumerable<IntRange> ranges, string description = null) {
            this.ranges = ranges;
            this.description = description;
        }

        public IntList(int size, IntRange range, string description = null) {
            this.description = description;

            var arrayRanges = new IntRange[size];
            for (int i = 0; i < size; i++) {
                arrayRanges[i] = range;
            }

            ranges = arrayRanges;
        }
    }
}