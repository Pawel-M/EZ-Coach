using UnityEngine;

namespace EZCoach.Pong {
    [RequireComponent(typeof(Rigidbody2D))]
    public class Ball : MonoBehaviour {
        private new Rigidbody2D rigidbody2D;

        void Awake() {
            rigidbody2D = GetComponent<Rigidbody2D>();
        }

        void Start() {
            Game.Round.RegisterBall(this);
        }

        public void Initialize(Vector2 startPosition, BallDirection direction) {
            rigidbody2D.position = startPosition;
            rigidbody2D.velocity = direction.ToVector2() * Game.BallSpeed;
        }
        
        public void Stop() {
            rigidbody2D.velocity = Vector2.zero;
        }

        private void CheckKill() {
            if (rigidbody2D.position.x <= Game.Round.LeftKill) {
                Game.Round.PlayerWon(PlayerNumber.Right);

            } else if (rigidbody2D.position.x >= Game.Round.RightKill) {
                Game.Round.PlayerWon(PlayerNumber.Left);
            }
        }
        public Vector2 Position => rigidbody2D.position;
        public Vector2 Velocity => rigidbody2D.velocity;
    }
}