const INSTANCE_ENDPOINT = "https://venus.aisandbox.ugbu.oraclepdemos.com/app1";

export async function sendMessage(message: string) {
    try {
        const url = new URL(`${INSTANCE_ENDPOINT}/get-super-daily`);

        url.searchParams.append("query", message); // pass message as query param

        const response = await fetch(url.toString())

        console.log(response)

        if (!response.ok) {
            throw new Error("Network response was not ok");
        }

        const data = await response.json();
        console.log(data.result)
        return data; // expects { result: "..." }
    } catch (error: any) {
        console.error("Error sending message:", error);
        return { result: `Error: ${error.message}` };
    }
}

/* 
try {
    const response = await fetch(`${NGROK_URL}/your-endpoint`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error sending message:", error);
    return { error: error.message };
  }
*/