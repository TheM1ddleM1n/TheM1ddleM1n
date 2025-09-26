const { basename } = require("node:path");

function getGithubToken() {
  const token = process.env.GH_TOKEN;
  if (!token) {
    throw new Error("GH_TOKEN environment variable is not set.");
  }
  return token;
}

async function getNotifications(since) {
  const response = await fetch(`https://api.github.com/notifications?all=true&since=${since}`, {
    headers: {
      'Accept': 'application/vnd.github+json',
      'Authorization': `Bearer ${getGithubToken()}`,
      'X-GitHub-Api-Version': '2022-11-28',
    },
  });
  return response.json();
}

async function shouldIncludeNotificationForRemoval(notification) {
  const response = await fetch(`https://api.github.com/repos/${notification.repository.full_name}`, {
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${getGithubToken()}`,
      "X-GitHub-Api-Version": "2022-11-28",
    },
  });
  return response.status === 404;
}

async function markNotificationRead(notification) {
  const response = await fetch(notification.url, {
    method: "PATCH",
    headers: {
      "Authorization": `Bearer ${getGithubToken()}`,
      "Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
    },
  });
  if (!response.ok) {
    console.error(`Failed to mark as read: ${response.status} ${response.statusText}`);
  }
}

async function markNotificationDone(notification) {
  const response = await fetch(notification.url, {
    method: "DELETE",
    headers: {
      "Authorization": `Bearer ${getGithubToken()}`,
      "Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
    },
  });
  if (!response.ok) {
    console.error(`Failed to mark as done: ${response.status} ${response.statusText}`);
  }
}

async function unsubscribe(notification) {
  const response = await fetch(notification.subscription_url, {
    method: "DELETE",
    headers: {
      "Authorization": `Bearer ${getGithubToken()}`,
      "Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
    },
  });
  if (!response.ok) {
    console.error(`Failed to unsubscribe: ${response.status} ${response.statusText}`);
  }
}

async function main() {
  const since = process.argv[2];
  if (!since) {
    console.error(`Usage: ${basename(process.argv[0])} ${basename(process.argv[1])} <since>`);
    process.exit(1);
  }

  try {
    new Date(since);
  } catch {
    console.error(`${since} is not a valid ISO 8601 date.`);
    process.exit(1);
  }

  const notifications = await getNotifications(since);
  for (const notification of notifications) {
    if (await shouldIncludeNotificationForRemoval(notification)) {
      console.log(`Cleaning up: ${notification.repository.full_name}`);
      await markNotificationRead(notification);
      await markNotificationDone(notification);
      await unsubscribe(notification);
    }
  }
  console.log("Cleanup complete.");
}

main().catch(console.error);
