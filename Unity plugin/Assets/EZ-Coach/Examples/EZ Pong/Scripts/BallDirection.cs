using UnityEngine;

namespace EZCoach.Pong {
    public enum BallDirection {
        UpRight = 0,
        UpLeft = 1,
        DownRight = 2,
        DownLeft = 3
    }

    public static class BallDirectionMethods {
        private static readonly Vector2[] VECTOR2S = new[] {
            new Vector2(1f, 1f).normalized, // Up-Right
            new Vector2(-1f, 1f).normalized, // Up-Left
            new Vector2(1f, -1f).normalized, // Down-Right
            new Vector2(-1f, -1f).normalized, // Down-Left
        };
        
        public static BallDirection Reflected(this BallDirection direction) {
            switch (direction) {
                case BallDirection.DownLeft:
                    return BallDirection.UpRight;

                case BallDirection.DownRight:
                    return BallDirection.UpLeft;

                case BallDirection.UpLeft:
                    return BallDirection.DownRight;

                case BallDirection.UpRight:
                    return BallDirection.DownLeft;
            }

            return BallDirection.DownLeft;
        }

        public static BallDirection ReflectedHorizontally(this BallDirection direction) {
            switch (direction) {
                case BallDirection.DownLeft:
                    return BallDirection.DownRight;

                case BallDirection.DownRight:
                    return BallDirection.DownLeft;

                case BallDirection.UpLeft:
                    return BallDirection.UpRight;

                case BallDirection.UpRight:
                    return BallDirection.UpLeft;
            }

            return BallDirection.DownLeft;
        }

        public static BallDirection ReflectedVertically(this BallDirection direction) {
            switch (direction) {
                case BallDirection.DownLeft:
                    return BallDirection.UpLeft;

                case BallDirection.DownRight:
                    return BallDirection.UpRight;

                case BallDirection.UpLeft:
                    return BallDirection.DownLeft;

                case BallDirection.UpRight:
                    return BallDirection.DownRight;
            }

            return BallDirection.DownLeft;
        }

        public static Vector2 ToVector2(this BallDirection direction) {
            return VECTOR2S[(int) direction];
        }
    }
}