<template>
  <ion-page>
  <div class="m-3 flex flex-row items-center justify-center">
    <Card title="Login to Frappe Live!" class="w-full max-w-md mt-4">
      <form class="flex flex-col space-y-2 w-full" @submit.prevent="submit">
        <Input
          required
          name="email"
          type="text"
          placeholder="johndoe@email.com"
          label="User ID"
        />
        <Input
          required
          name="password"
          type="password"
          placeholder="••••••"
          label="Password"
        />
        <Button :loading="session.login.loading" variant="solid"
          >Login</Button
        >
      </form>
    </Card>
  </div>
  </ion-page>
</template>

<script lang="ts" setup>
import { session } from '../data/session'
import { IonPage } from '@ionic/vue';

 

function submit(e: Event) {
  let formData = new FormData(e.target as HTMLFormElement)
  session.login.submit({
    email: formData.get('email') as string,
    password: formData.get('password') as string,
  })
}
</script>