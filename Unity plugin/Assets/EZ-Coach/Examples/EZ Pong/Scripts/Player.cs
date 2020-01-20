using UnityEngine;

namespace EZCoach.Pong {

    [RequireComponent(typeof(Rigidbody2D))]
    public class Player : MonoBehaviour {

        [SerializeField] private new GameObject renderer;
        [SerializeField] private PlayerNumber number;
        [SerializeField] private float height;

        private new Rigidbody2D rigidbody2D;
        private int halfHeight;
        private float nextTickTime = 0;
        private Vector2 startingPosition;
        private int numBounces = 0;

        void Awake() {
            rigidbody2D = GetComponent<Rigidbody2D>();
            startingPosition = rigidbody2D.position;
            halfHeight = Mathf.FloorToInt(height / 2);

            var localScale = renderer.transform.localScale;
            localScale.y = height;
            renderer.transform.localScale = localScale;
            InputDirection = PlayerDirection.None;
        }

        void Start() {
            Game.Round.RegisterPlayer(this);
        }

        public void Prepare(int y) {
            rigidbody2D.position = new Vector2(startingPosition.x, y);
            InputDirection = PlayerDirection.None;
            numBounces = 0;
        }

        void FixedUpdate() {
            if (InputDirection == PlayerDirection.None)
                return;

            var nextPosition = rigidbody2D.position;
            var moveDistance = Game.PlayerSpeed * Time.fixedDeltaTime;
            if (InputDirection == PlayerDirection.Up) {
                nextPosition.y = Mathf.Min(nextPosition.y + moveDistance, Game.Round.TopWall - halfHeight);
            } else if (InputDirection == PlayerDirection.Down) {
                nextPosition.y = Mathf.Max(nextPosition.y - moveDistance, Game.Round.BottomWall + halfHeight);
            }

            rigidbody2D.MovePosition(nextPosition);
        }

        private void OnCollisionEnter2D(Collision2D other) {
            if (!other.gameObject.name.Equals("Ball"))
                return;
            
            numBounces++;
            var bouncePosition = other.rigidbody.position.y - rigidbody2D.position.y;
            if (Mathf.Abs(bouncePosition) < Game.PlayerDeadBounceZone)
                return;

            var otherVelocity = other.rigidbody.velocity;
            var velocityYChange = Mathf.Sign(bouncePosition) * (Mathf.Abs(bouncePosition) - Game.PlayerDeadBounceZone) * Game.PlayerBounceChange;
            otherVelocity.y += velocityYChange;
            other.rigidbody.velocity = otherVelocity;
        }

        public PlayerNumber Number => number;
        public float Height => height;
        public float HalfHeight => halfHeight;
        public float Top => rigidbody2D.position.y + halfHeight;
        public float Bottom => rigidbody2D.position.y - halfHeight;
        public Vector2 Position => rigidbody2D.position;
        public PlayerDirection InputDirection { get; set; }

        public int NumBounces => numBounces;
    }
}