const MS_ENDPOINT = "https://r619jhnt-8001.usw3.devtunnels.ms";

export async function sendMessage(message: string) {
    try {
        const url = new URL(`${MS_ENDPOINT}/get-super-daily`);

        url.searchParams.append("query", message); // pass message as query param

        console.log(url.toString())

        const response = await fetch(url.toString(),{
          headers: {
            "x-api-key": ""
          }
        })

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