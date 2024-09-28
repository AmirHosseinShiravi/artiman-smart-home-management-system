- mqtt client multiple example: [link](https://github.com/emqx/MQTT-Client-Examples/tree/master)
- config load balancer: [document](https://docs.emqx.com/en/emqx/latest/deploy/cluster/lb.html), [github](https://github.com/emqx/emqx-usage-example/tree/main)

- we have error when try migrate dashboard HomeUser model, so after run makemigrations, we need to delete the homeUser addfield  in created migration file and then run migrate command to
don't get error.

- a lot of HABApp module code were changed, so we need to update module when install it in destination machine with what we have in this repo.
