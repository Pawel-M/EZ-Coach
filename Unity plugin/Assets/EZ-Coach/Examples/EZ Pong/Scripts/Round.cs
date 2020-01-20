using System.Linq;
using UnityEngine;
using UnityEngine.Events;

namespace EZCoach.Pong {
    public class Round : MonoBehaviour {

        [SerializeField] private int halfWidth;
        [SerializeField] private int halfHeight;
        [SerializeField] private int winningScore = 1;

        public UnityEvent pointsChangedEvent;
        public UnityEvent runningChangedEvent;

        private int topWall;
        private int bottomWall;
        private int leftKill;
        private int rightKill;
        private int[] playersPoints;
        private Player[] players;
        private Ball ball;
        private int[] bouncesByPlayers;
        private int[] totallBouncesByPlayers;
        private bool startBallRight = false;
        private bool running = false;

        void Awake() {
            topWall = halfHeight;
            bottomWall = -halfHeight;
            rightKill = halfWidth;
            leftKill = -halfWidth;
            playersPoints = new[] { 0, 0 };
            players = new Player[2];
            bouncesByPlayers = new[] {0, 0};
            totallBouncesByPlayers = new[] {0, 0};
        }

        void Start() {
            ResetGame();
        }

        public void ResetGame() {
            bouncesByPlayers[0] = 0;
            bouncesByPlayers[1] = 0;
            totallBouncesByPlayers[0] = 0;
            totallBouncesByPlayers[1] = 0;
            playersPoints[0] = 0;
            playersPoints[1] = 0;
            startBallRight = Random.Range(0f, 1f) < .5f;
        }

        public void RegisterPlayer(Player player) {
            players[(int)player.Number] = player;
        }

        public void RegisterBall(Ball ball) {
            this.ball = ball;
        }

        public void StartRound() {
            BallDirection direction;
            if (startBallRight) {
                direction = Random.Range(0f, 1f) < .5f ? BallDirection.DownRight : BallDirection.UpRight;
            } else {
                direction = Random.Range(0f, 1f) < .5f ? BallDirection.DownLeft : BallDirection.UpLeft;
            }

            ball.Initialize(Vector2.zero, direction);
            startBallRight = !startBallRight;
            players[(int)PlayerNumber.Left].Prepare(0);
            players[(int)PlayerNumber.Right].Prepare(0);
            bouncesByPlayers[(int) PlayerNumber.Left] = 0;
            bouncesByPlayers[(int) PlayerNumber.Right] = 0;

            pointsChangedEvent.Invoke();
            running = true;
            runningChangedEvent.Invoke();
        }

        private BallDirection GetRandomMoveDirection() {
            return (BallDirection) Random.Range(0, 4);
        }

        public void BallBouncedByPlayer(int playerNumber) {
            bouncesByPlayers[playerNumber]++;
            totallBouncesByPlayers[playerNumber]++;

            if (bouncesByPlayers[playerNumber] >= 100) {
                playersPoints[(int) PlayerNumber.Left]++;
                playersPoints[(int) PlayerNumber.Right]++;
                pointsChangedEvent.Invoke();
                StartRound();
            }
        }

        public void PlayerWon(PlayerNumber number) {
            playersPoints[(int)number]++;
            pointsChangedEvent.Invoke();
            ball.Stop();

            if (playersPoints.Max() >= winningScore) {
                Debug.Log($"Round ended {playersPoints[0]} : {playersPoints[1]}");
                running = false;
                runningChangedEvent.Invoke();
            } else {
                StartRound();
            }
        }

        public void StopRound() {
            ball.Stop();
            Debug.Log($"Round stopped");
            running = false;
            runningChangedEvent.Invoke();
        }

        public int TopWall => topWall;
        public int BottomWall => bottomWall;
        public int LeftKill => leftKill;
        public int RightKill => rightKill;
        public int LeftPlayerPoints => playersPoints[(int)PlayerNumber.Left];
        public int RightPlayerPoints => playersPoints[(int)PlayerNumber.Right];
        public Player[] Players => players;
        public Ball Ball => ball;
        public int[] BallBouncesByPlayers => totallBouncesByPlayers;

        public bool Running => running;
    }
}