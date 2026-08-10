export default function ChatHistory() {

    return (
        <div className="p-4 w-full">
            <h2 className="text-lg font-semibold mb-4">
                Chat History
            </h2>

            {props.history?.length === 0 && (
                <p className="text-sm opacity-60">
                    No questions yet
                </p>
            )}

            {props.history?.map((turn, index) => (
                <div
                    key={index}
                    className="mb-3 p-3 rounded-lg bg-muted"
                >
                    <div className="text-xs opacity-60 mb-1">
                        {index + 1}
                    </div>

                    <div className="text-sm">
                        {turn.question}
                    </div>
                </div>
            ))}
        </div>
    );
}