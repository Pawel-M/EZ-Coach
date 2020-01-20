using System;

namespace EZCoach.GridWorld {
    [Serializable]
    public struct IntVector2 {
        public int x, y;

        public IntVector2 SetX(int x) {
            return new IntVector2 {x = x, y = y};
        }

        public IntVector2 SetY(int y) {
            return new IntVector2 {x = x, y = y};
        }

        public IntVector2 AddX(int value) {
            return new IntVector2 {x = x + value, y = y};
        }

        public IntVector2 AddY(int value) {
            return new IntVector2 {x = x, y = y + value};
        }

        public override bool Equals(object obj) {
            if (!(obj is IntVector2)) {
                throw new ArgumentException("obj is not an IntVector2 instance.");
            }

            return this == (IntVector2) obj;
        }

        public bool Equals(IntVector2 other) {
            return this == other;
        }

        public override int GetHashCode() {
            unchecked {
                return (x * 397) ^ y;
            }
        }

        public static bool operator ==(IntVector2 first, IntVector2 second) {
            return first.x == second.x && first.y == second.y;
        }

        public static bool operator !=(IntVector2 first, IntVector2 second) {
            return !(first == second);
        }

        public override string ToString() {
            return "{" + x + ", " + y + "}";
        }
    }
}