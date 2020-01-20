using UnityEngine;

namespace EZCoach.Pong {
    public struct IntVector2 {
        public int x, y;

        public IntVector2(int x, int y) {
            this.x = x;
            this.y = y;
        }

        public static explicit operator IntVector2(Vector2 vector2) {
            return new IntVector2((int)vector2.x, (int)vector2.y);
        }

        public static implicit operator Vector2(IntVector2 intVector2) {
            return new Vector2(intVector2.x, intVector2.y);
        }
    }
}